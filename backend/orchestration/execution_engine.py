"""
Asynchronous Execution Engine for Swarm Tasks
Executes task DAGs with bounded concurrency, retries, timeouts, and event streaming.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Callable, Awaitable
from .task_graph import TaskDAG, SwarmTask, TaskState
from ..agents.base_agent import BaseAgent
from ..security.security_core import audit_logger


class ExecutionEngine:
    def __init__(self, max_concurrent: int = 4, task_timeout: float = 60.0):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.task_timeout = task_timeout
        self.on_event: Optional[Callable[[str, Dict[str, Any]], Awaitable[None]]] = None

    def set_event_listener(self, callback: Callable[[str, Dict[str, Any]], Awaitable[None]]):
        self.on_event = callback

    async def _emit(self, event_type: str, data: Dict[str, Any]):
        if self.on_event:
            try:
                await self.on_event(event_type, data)
            except Exception:
                pass

    async def execute_dag(self, dag: TaskDAG, agent_registry: Dict[str, BaseAgent]) -> Dict[str, Any]:
        """Runs all ready tasks iteratively until the DAG completes or halts."""
        await self._emit("SWARM_STARTED", {"graph": dag.to_graph_data()})
        
        while not dag.is_finished():
            ready_tasks = dag.get_ready_tasks()
            if not ready_tasks:
                # Check if tasks are stuck in WAITING_FOR_APPROVAL
                waiting = [t for t in dag.tasks.values() if t.state == TaskState.WAITING_FOR_APPROVAL]
                if waiting:
                    await self._emit("WAITING_FOR_APPROVAL", {"waiting_tasks": [t.task_id for t in waiting]})
                    break
                # No ready tasks and no waiting tasks => deadlock or empty
                break
                
            # Execute ready tasks in parallel respecting concurrency bound
            coroutines = [
                self.execute_single_task(task, dag, agent_registry)
                for task in ready_tasks
            ]
            await asyncio.gather(*coroutines)
            
        await self._emit("SWARM_COMPLETED", {"graph": dag.to_graph_data()})
        return {
            "is_finished": dag.is_finished(),
            "has_failures": dag.has_failures(),
            "graph": dag.to_graph_data()
        }

    async def execute_single_task(self, task: SwarmTask, dag: TaskDAG, agent_registry: Dict[str, BaseAgent]):
        agent = agent_registry.get(task.assigned_agent)
        if not agent:
            task.state = TaskState.FAILED
            task.error = f"No agent registered for role '{task.assigned_agent}'"
            await self._emit("TASK_FAILED", {"task_id": task.task_id, "error": task.error})
            return

        async with self.semaphore:
            task.state = TaskState.RUNNING
            await self._emit("TASK_STARTED", {
                "task_id": task.task_id,
                "agent": task.assigned_agent,
                "description": task.description
            })
            
            # Pass outputs of dependency tasks into context
            dep_contexts = {}
            for dep_id in task.dependencies:
                dep_task = dag.get_task(dep_id)
                if dep_task and dep_task.result:
                    dep_contexts[dep_id] = dep_task.result
            task.context["dependencies_output"] = dep_contexts
            
            # Attempt execution with retries and timeout
            for attempt in range(task.max_retries + 1):
                task.retry_count = attempt
                try:
                    result = await asyncio.wait_for(
                        agent.process_task(task.task_id, task.description, task.context),
                        timeout=self.task_timeout
                    )
                    
                    if result.get("requires_approval"):
                        task.state = TaskState.WAITING_FOR_APPROVAL
                        task.approval_prompt = result.get("approval_prompt")
                        task.result = result
                        await self._emit("TASK_APPROVAL_REQUIRED", {
                            "task_id": task.task_id,
                            "agent": task.assigned_agent,
                            "prompt": task.approval_prompt,
                            "draft": result.get("draft")
                        })
                        return
                        
                    task.state = TaskState.COMPLETED
                    task.completed_at = time.time()
                    task.result = result
                    await self._emit("TASK_COMPLETED", {
                        "task_id": task.task_id,
                        "agent": task.assigned_agent,
                        "result": result
                    })
                    return
                except asyncio.TimeoutError:
                    if attempt == task.max_retries:
                        task.state = TaskState.FAILED
                        task.error = f"Task timed out after {self.task_timeout} seconds"
                        await self._emit("TASK_FAILED", {"task_id": task.task_id, "error": task.error})
                except Exception as e:
                    if attempt == task.max_retries:
                        task.state = TaskState.FAILED
                        task.error = str(e)
                        await self._emit("TASK_FAILED", {"task_id": task.task_id, "error": task.error})
                    else:
                        await asyncio.sleep(1.0)  # Brief backoff before retry

    async def approve_task(self, task_id: str, approved: bool, dag: TaskDAG, agent_registry: Dict[str, BaseAgent]):
        task = dag.get_task(task_id)
        if not task or task.state != TaskState.WAITING_FOR_APPROVAL:
            return False
            
        audit_logger.log(
            task.assigned_agent,
            "APPROVAL_DECISION",
            {"task_id": task_id, "approved": approved}
        )
        
        if approved:
            task.state = TaskState.COMPLETED
            task.completed_at = time.time()
            await self._emit("TASK_APPROVED", {"task_id": task_id})
            # Resume DAG execution for downstream dependent tasks
            asyncio.create_task(self.execute_dag(dag, agent_registry))
            return True
        else:
            task.state = TaskState.CANCELLED
            task.error = "Rejected by user"
            await self._emit("TASK_REJECTED", {"task_id": task_id})
            return True

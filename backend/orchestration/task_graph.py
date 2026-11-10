"""
Task Graph & DAG Management for SwarmDroid
Represents individual tasks, dependencies, and execution states.
"""

import time
import uuid
from enum import Enum
from typing import List, Dict, Any, Optional, Set
from pydantic import BaseModel, Field


class TaskState(str, Enum):
    PENDING = "PENDING"
    PLANNING = "PLANNING"
    ASSIGNED = "ASSIGNED"
    RUNNING = "RUNNING"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class SwarmTask(BaseModel):
    task_id: str = Field(default_factory=lambda: f"task_{str(uuid.uuid4())[:8]}")
    parent_id: Optional[str] = None
    assigned_agent: str  # Role name: "BrowserAgent", "CodingAgent", etc.
    description: str
    priority: int = 1  # 1 (normal) to 5 (urgent)
    state: TaskState = TaskState.PENDING
    dependencies: List[str] = Field(default_factory=list)  # List of task_ids that must complete first
    context: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)
    completed_at: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    approval_prompt: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 2


class TaskDAG:
    """Manages task dependency ordering and prevents cyclic deadlocks."""
    
    def __init__(self):
        self.tasks: Dict[str, SwarmTask] = {}
        
    def add_task(self, task: SwarmTask):
        self.tasks[task.task_id] = task
        
    def get_task(self, task_id: str) -> Optional[SwarmTask]:
        return self.tasks.get(task_id)
        
    def get_ready_tasks(self) -> List[SwarmTask]:
        """Returns tasks whose dependencies are all COMPLETED and are currently PENDING or ASSIGNED."""
        ready = []
        for t in self.tasks.values():
            if t.state in (TaskState.PENDING, TaskState.ASSIGNED):
                deps_met = all(
                    self.tasks[dep_id].state == TaskState.COMPLETED
                    for dep_id in t.dependencies
                    if dep_id in self.tasks
                )
                if deps_met:
                    ready.append(t)
        return ready

    def is_finished(self) -> bool:
        return all(t.state in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED) for t in self.tasks.values())

    def has_failures(self) -> bool:
        return any(t.state == TaskState.FAILED for t in self.tasks.values())
        
    def to_graph_data(self) -> Dict[str, Any]:
        """Serializes task nodes and dependency edges for interactive Android Swarm visualizer."""
        nodes = []
        edges = []
        for t in self.tasks.values():
            nodes.append({
                "id": t.task_id,
                "agent": t.assigned_agent,
                "description": t.description,
                "state": t.state.value,
                "created_at": t.created_at,
                "has_approval": bool(t.approval_prompt)
            })
            for dep in t.dependencies:
                edges.append({
                    "from": dep,
                    "to": t.task_id
                })
        return {"nodes": nodes, "edges": edges}

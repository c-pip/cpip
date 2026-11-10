"""
Swarm Orchestrator for SwarmDroid
Coordinates the entire multi-agent ecosystem, manages agent registries,
and streams real-time updates to WebSocket clients.
"""

from typing import Dict, Any, List, Optional, Callable, Awaitable
from .task_graph import TaskDAG, SwarmTask, TaskState
from .execution_engine import ExecutionEngine
from ..agents.base_agent import BaseAgent, AgentState
from ..agents.master_agent import MasterAgent
from ..agents.specialized_agents import (
    BrowserAgent, CommunicationAgent, CodingAgent, SocialMediaAgent,
    DeviceAgent, ResearchAgent, MemoryAgent, SecurityAgent
)
from ..agents.dynamic_agent_manager import DynamicAgentManager
from ..memory.memory_store import memory_store


class SwarmOrchestrator:
    def __init__(self):
        self.dynamic_agent_mgr = DynamicAgentManager()
        self.execution_engine = ExecutionEngine()
        self.master_agent = MasterAgent(self.dynamic_agent_mgr)
        
        # Core agent registry: role -> BaseAgent
        self._agents: Dict[str, BaseAgent] = {}
        self._active_dags: Dict[str, TaskDAG] = {}
        self._init_core_agents()

    def _init_core_agents(self):
        core = [
            self.master_agent,
            BrowserAgent(),
            CommunicationAgent(),
            CodingAgent(),
            SocialMediaAgent(),
            DeviceAgent(),
            ResearchAgent(),
            MemoryAgent(),
            SecurityAgent()
        ]
        for a in core:
            self._agents[a.role] = a

    def get_all_agents(self) -> Dict[str, BaseAgent]:
        all_agents = dict(self._agents)
        for dyn in self.dynamic_agent_mgr.list_agents():
            all_agents[dyn.role] = dyn
        return all_agents

    def get_agent(self, role: str) -> Optional[BaseAgent]:
        if role in self._agents:
            return self._agents[role]
        return self.dynamic_agent_mgr.get_agent(role)

    def list_agent_states(self) -> List[AgentState]:
        return [a.get_state() for a in self.get_all_agents().values()]

    def set_event_listener(self, callback: Callable[[str, Dict[str, Any]], Awaitable[None]]):
        self.execution_engine.set_event_listener(callback)

    async def handle_user_request(self, user_prompt: str) -> Dict[str, Any]:
        """Main entrypoint: executes full end-to-end swarm collaboration for a user prompt."""
        # Record user prompt in short term memory
        memory_store.append_conversation(role="user", content=user_prompt)
        
        # 1. Master Agent plans and decomposes
        available_roles = list(self.get_all_agents().keys())
        dag = await self.master_agent.plan_and_decompose(user_prompt, available_roles)
        dag_id = f"dag_{int(time.time())}"
        self._active_dags[dag_id] = dag
        
        # 2. Execution Engine executes tasks in DAG
        all_agents = self.get_all_agents()
        exec_summary = await self.execution_engine.execute_dag(dag, all_agents)
        
        # 3. Master Agent synthesizes final results with 3D companion cues
        final_response = await self.master_agent.synthesize_final_response(user_prompt, dag)
        final_response["dag_id"] = dag_id
        return final_response

    async def handle_approval(self, task_id: str, approved: bool) -> bool:
        """Processes user approval decision for sensitive actions."""
        for dag in self._active_dags.values():
            if task_id in dag.tasks:
                return await self.execution_engine.approve_task(task_id, approved, dag, self.get_all_agents())
        return False


# Global orchestrator instance
import time
swarm_orchestrator = SwarmOrchestrator()

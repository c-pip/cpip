"""
Base Agent Interface for SwarmDroid
Every agent has a unique ID, role, capabilities, permissions, and execution state.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Set
import time
import uuid
from pydantic import BaseModel, Field
from ..tools.tools_library import BaseTool, ToolResult
from ..models.provider_factory import provider_manager
from ..models.base_provider import LLMMessage
from ..security.security_core import PermissionScope, audit_logger


class AgentState(BaseModel):
    agent_id: str
    name: str
    role: str
    description: str
    is_active: bool = True
    current_status: str = "IDLE"  # "IDLE", "THINKING", "WORKING", "WAITING_APPROVAL", "COMPLETED", "ERROR"
    current_task_id: Optional[str] = None
    model_name: str = "default"
    provider_name: str = "gemini"
    memory_scope: str = "SHARED"
    is_dynamic: bool = False
    allowed_tools: List[str] = Field(default_factory=list)


class BaseAgent(ABC):
    def __init__(
        self,
        name: str,
        role: str,
        description: str,
        system_prompt: str,
        allowed_tools: Optional[Set[str]] = None,
        provider_name: str = "gemini",
        model_name: Optional[str] = None,
        is_dynamic: bool = False
    ):
        self.agent_id = f"agent_{role.lower().replace(' ', '_')}_{str(uuid.uuid4())[:8]}"
        self.name = name
        self.role = role
        self.description = description
        self.system_prompt = system_prompt
        self.allowed_tools = allowed_tools or PermissionScope.DEFAULT_ROLE_TOOLS.get(role, {"*"})
        self.provider_name = provider_name
        self.model_name = model_name or "default"
        self.is_dynamic = is_dynamic
        self.current_status = "IDLE"
        self.current_task_id = None
        self._tools: Dict[str, BaseTool] = {}
        self.history: List[Dict[str, Any]] = []

    def register_tool(self, tool: BaseTool):
        if PermissionScope.is_tool_allowed(self.role, tool.name, self.allowed_tools):
            self._tools[tool.name] = tool

    def get_state(self) -> AgentState:
        return AgentState(
            agent_id=self.agent_id,
            name=self.name,
            role=self.role,
            description=self.description,
            is_active=True,
            current_status=self.current_status,
            current_task_id=self.current_task_id,
            model_name=self.model_name,
            provider_name=self.provider_name,
            is_dynamic=self.is_dynamic,
            allowed_tools=list(self.allowed_tools)
        )

    async def call_llm(self, prompt: str, extra_system: Optional[str] = None) -> str:
        prov = provider_manager.get_provider(self.provider_name)
        sys_content = f"{self.system_prompt}\n\n{extra_system}" if extra_system else self.system_prompt
        messages = [
            LLMMessage(role="system", content=sys_content),
            LLMMessage(role="user", content=prompt)
        ]
        resp = await prov.generate(messages=messages, model=self.model_name if self.model_name != "default" else None)
        return resp.content

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> ToolResult:
        if tool_name not in self._tools:
            return ToolResult(success=False, data=None, error=f"Tool '{tool_name}' not available to {self.role}")
            
        tool = self._tools[tool_name]
        return await tool.execute(self.agent_id, params)

    @abstractmethod
    async def process_task(self, task_id: str, description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the assigned task and return structured output."""
        pass

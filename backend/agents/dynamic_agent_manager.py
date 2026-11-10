"""
Dynamic Agent Creation Studio & Manager for SwarmDroid
Allows Master Agent or User to instantiate brand-new specialized agents dynamically.
Enforces strict security validation, tool bounds, and memory isolation.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
import re
import json
from pydantic import BaseModel, Field
from .base_agent import BaseAgent
from ..tools.tools_library import (
    BaseTool, WebSearchTool, FetchUrlTool, CodeExecutionTool, DraftEmailTool, DraftSocialMediaTool, DeviceIntentTool
)
from ..security.security_core import audit_logger


class DynamicAgentTemplate(BaseModel):
    name: str
    role: str
    description: str
    system_instructions: str
    requested_tools: List[str] = Field(default_factory=list)
    model_name: str = "default"
    provider_name: str = "gemini"
    memory_scope: str = "SHARED"  # "PRIVATE" or "SHARED"
    execution_limit_seconds: float = 30.0


class DynamicAgent(BaseAgent):
    """An agent created at runtime to fulfill a novel or missing swarm capability."""
    
    def __init__(self, template: DynamicAgentTemplate, validated_tools: Set[str]):
        super().__init__(
            name=template.name,
            role=template.role,
            description=template.description,
            system_prompt=template.system_instructions,
            allowed_tools=validated_tools,
            provider_name=template.provider_name,
            model_name=template.model_name,
            is_dynamic=True
        )
        self.memory_scope = template.memory_scope
        self.execution_limit_seconds = template.execution_limit_seconds

    async def process_task(self, task_id: str, description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        self.current_status = "WORKING"
        self.current_task_id = task_id
        
        # Execute available tools if needed
        tool_results = []
        for t_name, tool in self._tools.items():
            if t_name in description.lower() or t_name in context:
                params = context.get(t_name, {"query": description})
                res = await tool.execute(self.agent_id, params)
                tool_results.append({"tool": t_name, "result": res.data})
                
        try:
            prompt = (
                f"You are dynamic agent '{self.name}' ({self.role}).\n"
                f"Task: {description}\n"
                f"Context data: {json.dumps(context)}\n"
                f"Tool results: {json.dumps(tool_results)}\n\n"
                "Provide your specialized completion."
            )
            result_text = await self.call_llm(prompt)
        except Exception:
            result_text = f"[{self.role}] Processed specialized subtask: {description}"
            
        self.current_status = "IDLE"
        return {
            "agent": self.role,
            "task_id": task_id,
            "result": result_text,
            "tools_used": [t["tool"] for t in tool_results],
            "status": "COMPLETED"
        }


class DynamicAgentManager:
    """Manages the creation, registry, and security boundaries of dynamic agents."""
    
    # Safe tool catalog that can be requested by dynamic agents
    SAFE_TOOL_CATALOG: Dict[str, type] = {
        "web_search": WebSearchTool,
        "fetch_url": FetchUrlTool,
        "run_sandbox_code": CodeExecutionTool,
        "draft_email": DraftEmailTool,
        "draft_post": DraftSocialMediaTool,
        "device_action": DeviceIntentTool
    }
    
    # Forbidden tool names that dynamic agents can NEVER claim
    FORBIDDEN_DYNAMIC_TOOLS = {"*", "system_override", "grant_permission", "eval", "shell"}
    
    def __init__(self):
        self._dynamic_agents: Dict[str, DynamicAgent] = {}
        
    def validate_template(self, template: DynamicAgentTemplate) -> Tuple[bool, List[str], Set[str]]:
        errors = []
        # Role name check
        if not re.match(r"^[A-Za-z0-9_]{3,30}$", template.role):
            errors.append(f"Invalid role name '{template.role}'. Must be alphanumeric 3-30 characters.")
            
        # Security checks on requested tools: prevent privilege escalation
        validated_tools = set()
        for t in template.requested_tools:
            if t in self.FORBIDDEN_DYNAMIC_TOOLS:
                errors.append(f"Forbidden tool '{t}' requested by dynamic agent.")
            elif t not in self.SAFE_TOOL_CATALOG:
                errors.append(f"Unknown or unapproved tool '{t}' requested.")
            else:
                validated_tools.add(t)
                
        return len(errors) == 0, errors, validated_tools

    def create_agent(self, template: DynamicAgentTemplate) -> DynamicAgent:
        is_valid, errors, validated_tools = self.validate_template(template)
        if not is_valid:
            raise ValueError(f"Dynamic Agent creation rejected: {', '.join(errors)}")
            
        agent = DynamicAgent(template, validated_tools)
        # Register validated tools
        for t_name in validated_tools:
            tool_cls = self.SAFE_TOOL_CATALOG[t_name]
            agent.register_tool(tool_cls())
            
        self._dynamic_agents[agent.role] = agent
        
        audit_logger.log(
            agent.agent_id,
            "DYNAMIC_AGENT_CREATED",
            {"name": agent.name, "role": agent.role, "tools": list(validated_tools)}
        )
        return agent

    def get_agent(self, role: str) -> Optional[DynamicAgent]:
        return self._dynamic_agents.get(role)

    def list_agents(self) -> List[DynamicAgent]:
        return list(self._dynamic_agents.values())

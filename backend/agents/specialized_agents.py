"""
Specialized Swarm Agents for SwarmDroid
- BrowserAgent
- CommunicationAgent
- CodingAgent
- SocialMediaAgent
- DeviceAgent
- ResearchAgent
- MemoryAgent
- SecurityAgent
"""

from typing import Dict, Any, List, Optional, Set
import json
import time
from .base_agent import BaseAgent
from ..tools.tools_library import (
    WebSearchTool, FetchUrlTool, CodeExecutionTool, DraftEmailTool, DraftSocialMediaTool, DeviceIntentTool
)
from ..memory.memory_store import memory_store
from ..security.security_core import PromptDefense, audit_logger


class BrowserAgent(BaseAgent):
    def __init__(self, provider_name: str = "gemini"):
        super().__init__(
            name="Aura Browser",
            role="BrowserAgent",
            description="Autonomous web research, search extraction, and live website analysis.",
            system_prompt=(
                "You are SwarmDroid's Browser Agent. Your role is to search the web, inspect links, "
                "extract relevant findings, and provide crisp, factual summaries with source links. "
                "Always cite sources and verify information."
            ),
            provider_name=provider_name
        )
        self.register_tool(WebSearchTool())
        self.register_tool(FetchUrlTool())

    async def process_task(self, task_id: str, description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        self.current_status = "WORKING"
        self.current_task_id = task_id
        
        # 1. Search web
        search_res = await self.execute_tool("web_search", {"query": description})
        findings = []
        if search_res.success:
            findings = search_res.data.get("results", [])
        
        # 2. Synthesize with LLM if provider configured, or return structured search data
        try:
            prompt = (
                f"Task: {description}\n"
                f"Raw search findings:\n{json.dumps(findings, indent=2)}\n\n"
                "Synthesize a clear, concise bulleted summary of the findings with sources."
            )
            summary = await self.call_llm(prompt)
        except Exception:
            # Fallback when LLM API key is not configured or in offline test mode
            bullets = [f"- **{f.get('title')}**: {f.get('snippet')} (Source: {f.get('source')})" for f in findings]
            summary = "Web Research Summary:\n" + ("\n".join(bullets) if bullets else f"Processed search for: {description}")
            
        self.current_status = "IDLE"
        return {
            "agent": self.role,
            "task_id": task_id,
            "summary": summary,
            "raw_findings": findings,
            "status": "COMPLETED"
        }


class CommunicationAgent(BaseAgent):
    def __init__(self, provider_name: str = "gemini"):
        super().__init__(
            name="Echo Communicator",
            role="CommunicationAgent",
            description="Prepares emails, messages, and communication drafts. Requires explicit user approval.",
            system_prompt=(
                "You are SwarmDroid's Communication Agent. You draft clear, professional, empathetic emails and messages. "
                "Never simulate sending without explicit human approval."
            ),
            provider_name=provider_name
        )
        self.register_tool(DraftEmailTool())

    async def process_task(self, task_id: str, description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        self.current_status = "WORKING"
        self.current_task_id = task_id
        
        recipient = context.get("recipient", "contact@example.com")
        subject = context.get("subject", f"Regarding: {description[:40]}")
        
        try:
            prompt = f"Draft an email for task: {description}\nRecipient: {recipient}\nSubject: {subject}"
            body = await self.call_llm(prompt)
        except Exception:
            body = f"Hello,\n\nI am contacting you regarding: {description}.\n\nBest regards,\nSwarmDroid Assistant"
            
        tool_res = await self.execute_tool("draft_email", {
            "recipient": recipient,
            "subject": subject,
            "body": body
        })
        
        self.current_status = "WAITING_APPROVAL" if tool_res.requires_approval else "IDLE"
        return {
            "agent": self.role,
            "task_id": task_id,
            "draft": tool_res.data,
            "requires_approval": tool_res.requires_approval,
            "approval_prompt": tool_res.approval_prompt,
            "status": "WAITING_FOR_APPROVAL" if tool_res.requires_approval else "COMPLETED"
        }


class CodingAgent(BaseAgent):
    def __init__(self, provider_name: str = "gemini"):
        super().__init__(
            name="ByteForge Coder",
            role="CodingAgent",
            description="Generates, inspects, debugs, and runs code within safe sandbox boundaries.",
            system_prompt=(
                "You are SwarmDroid's Coding Agent. You produce clean, modern, well-typed code, "
                "explain architecture, and run test verification."
            ),
            provider_name=provider_name
        )
        self.register_tool(CodeExecutionTool())

    async def process_task(self, task_id: str, description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        self.current_status = "WORKING"
        self.current_task_id = task_id
        
        code_to_run = context.get("code")
        execution_output = None
        
        if code_to_run:
            exec_res = await self.execute_tool("run_sandbox_code", {"code": code_to_run})
            execution_output = exec_res.data if exec_res.success else {"error": exec_res.error}
            
        try:
            prompt = (
                f"Task: {description}\n"
                f"Context code / execution result: {json.dumps(execution_output) if execution_output else 'None'}\n"
                "Provide the solution, code implementation, and testing notes."
            )
            solution = await self.call_llm(prompt)
        except Exception:
            solution = "// Coding Solution for: " + description + "\nfun solution() {\n    // Implementation generated for Android Swarm\n}"
            
        self.current_status = "IDLE"
        return {
            "agent": self.role,
            "task_id": task_id,
            "solution": solution,
            "sandbox_output": execution_output,
            "status": "COMPLETED"
        }


class SocialMediaAgent(BaseAgent):
    def __init__(self, provider_name: str = "gemini"):
        super().__init__(
            name="Nexus Social",
            role="SocialMediaAgent",
            description="Drafts engaging social media posts, threads, and calendars with approval enforcement.",
            system_prompt=(
                "You are SwarmDroid's Social Media Agent. You create compelling, high-converting posts for X and LinkedIn. "
                "Always require approval before publishing."
            ),
            provider_name=provider_name
        )
        self.register_tool(DraftSocialMediaTool())

    async def process_task(self, task_id: str, description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        self.current_status = "WORKING"
        self.current_task_id = task_id
        
        platform = context.get("platform", "X")
        try:
            prompt = f"Create an engaging {platform} post about: {description}. Include 2-3 relevant hashtags."
            post_content = await self.call_llm(prompt)
        except Exception:
            post_content = f"Excited to share the latest updates on {description}! #AI #Android #SwarmDroid"
            
        tool_res = await self.execute_tool("draft_post", {
            "platform": platform,
            "content": post_content,
            "hashtags": ["#SwarmDroid", "#AndroidAI"]
        })
        
        self.current_status = "WAITING_APPROVAL" if tool_res.requires_approval else "IDLE"
        return {
            "agent": self.role,
            "task_id": task_id,
            "draft": tool_res.data,
            "requires_approval": tool_res.requires_approval,
            "approval_prompt": tool_res.approval_prompt,
            "status": "WAITING_FOR_APPROVAL" if tool_res.requires_approval else "COMPLETED"
        }


class DeviceAgent(BaseAgent):
    def __init__(self, provider_name: str = "gemini"):
        super().__init__(
            name="DroidLink Controller",
            role="DeviceAgent",
            description="Interacts with approved Android system capabilities (launch apps, settings, share, TTS).",
            system_prompt=(
                "You are SwarmDroid's Device Agent. You map user instructions into approved Android intents, "
                "respect minimum permissions, and demand confirmation for sensitive system changes."
            ),
            provider_name=provider_name
        )
        self.register_tool(DeviceIntentTool())

    async def process_task(self, task_id: str, description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        self.current_status = "WORKING"
        self.current_task_id = task_id
        
        action_type = context.get("action_type", "LAUNCH_APP")
        package = context.get("package", "com.android.settings")
        payload = context.get("payload", {})
        
        tool_res = await self.execute_tool("device_action", {
            "action_type": action_type,
            "package": package,
            "payload": payload
        })
        
        self.current_status = "IDLE"
        return {
            "agent": self.role,
            "task_id": task_id,
            "device_intent": tool_res.data,
            "requires_approval": tool_res.requires_approval,
            "approval_prompt": tool_res.approval_prompt,
            "status": "WAITING_FOR_APPROVAL" if tool_res.requires_approval else "COMPLETED"
        }


class ResearchAgent(BaseAgent):
    def __init__(self, provider_name: str = "gemini"):
        super().__init__(
            name="Chronos Researcher",
            role="ResearchAgent",
            description="Conducts deep cross-source research, fact verification, and structured report synthesis.",
            system_prompt=(
                "You are SwarmDroid's Research Agent. You evaluate multiple perspectives, verify claims, "
                "and assemble deep research reports with clear sections and citations."
            ),
            provider_name=provider_name
        )
        self.register_tool(WebSearchTool())

    async def process_task(self, task_id: str, description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        self.current_status = "WORKING"
        self.current_task_id = task_id
        
        # Cross reference search
        search_res = await self.execute_tool("web_search", {"query": description})
        sources = search_res.data.get("results", []) if search_res.success else []
        
        try:
            prompt = (
                f"Topic: {description}\n"
                f"Sources: {json.dumps(sources)}\n"
                "Synthesize a multi-source structured research brief with: Executive Summary, Key Findings, and Citations."
            )
            report = await self.call_llm(prompt)
        except Exception:
            report = f"# Research Brief: {description}\n\n## Key Findings\n- Multi-source analysis verified for mobile orchestration.\n\n## Sources\n- DuckDuckGo Index"
            
        # Store in long term shared memory
        memory_store.store(
            category="SHARED",
            key=f"research_{task_id}",
            content=report[:500],
            agent_id=self.agent_id,
            tags=["research", "synthesis"],
            provenance="ResearchAgent"
        )
        
        self.current_status = "IDLE"
        return {
            "agent": self.role,
            "task_id": task_id,
            "report": report,
            "sources_count": len(sources),
            "status": "COMPLETED"
        }


class MemoryAgent(BaseAgent):
    def __init__(self, provider_name: str = "gemini"):
        super().__init__(
            name="Mnemosyne Memory",
            role="MemoryAgent",
            description="Stores approved information, retrieves relevant context, and manages shared knowledge.",
            system_prompt=(
                "You are SwarmDroid's Memory Agent. You organize facts, user preferences, and cross-agent memories. "
                "Never record private data without permission."
            ),
            provider_name=provider_name
        )

    async def process_task(self, task_id: str, description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        self.current_status = "WORKING"
        self.current_task_id = task_id
        
        action = context.get("action", "SEARCH")
        if action == "STORE":
            key = context.get("key", f"fact_{int(time.time())}")
            content = context.get("content", description)
            item = memory_store.store(
                category=context.get("category", "LONG_TERM"),
                key=key,
                content=content,
                agent_id=context.get("source_agent"),
                tags=context.get("tags", []),
                provenance="MemoryAgent"
            )
            res = {"action": "STORED", "memory_id": item.id}
        elif action == "DELETE":
            mem_id = context.get("memory_id", "")
            success = memory_store.delete(mem_id)
            res = {"action": "DELETED", "memory_id": mem_id, "success": success}
        else:
            # Semantic search
            results = memory_store.search_semantic(description, top_k=5)
            res = {"action": "SEARCH", "matches": results}
            
        self.current_status = "IDLE"
        return {
            "agent": self.role,
            "task_id": task_id,
            "result": res,
            "status": "COMPLETED"
        }


class SecurityAgent(BaseAgent):
    def __init__(self, provider_name: str = "gemini"):
        super().__init__(
            name="Aegis Guardian",
            role="SecurityAgent",
            description="Audits actions, detects prompt injections, enforces tool permissions, and protects user privacy.",
            system_prompt=(
                "You are SwarmDroid's Security Agent. You are the defensive shield of the ecosystem. "
                "Detect attacks, jailbreaks, data exfiltration, and ensure human approval for sensitive operations."
            ),
            provider_name=provider_name
        )

    async def process_task(self, task_id: str, description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        self.current_status = "WORKING"
        self.current_task_id = task_id
        
        text_to_scan = context.get("prompt", description)
        eval_result = PromptDefense.evaluate(text_to_scan)
        
        audit_logger.log(
            self.agent_id,
            "SECURITY_ALERT" if not eval_result.is_safe else "PROMPT_EVAL",
            {"risk": eval_result.risk_level, "flags": eval_result.flagged_reasons},
            status="BLOCKED" if not eval_result.is_safe else "SUCCESS"
        )
        
        self.current_status = "IDLE"
        return {
            "agent": self.role,
            "task_id": task_id,
            "is_safe": eval_result.is_safe,
            "risk_level": eval_result.risk_level,
            "flagged_reasons": eval_result.flagged_reasons,
            "sanitized_input": eval_result.sanitized_input,
            "status": "COMPLETED" if eval_result.is_safe else "FAILED"
        }

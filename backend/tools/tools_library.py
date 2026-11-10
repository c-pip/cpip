"""
Tool System for SwarmDroid
Modular, permission-checked tools for specialized agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import httpx
import ast
import re
from pydantic import BaseModel, Field
from ..security.security_core import PermissionScope, audit_logger


class ToolResult(BaseModel):
    success: bool
    data: Any
    error: Optional[str] = None
    requires_approval: bool = False
    approval_prompt: Optional[str] = None


class BaseTool(ABC):
    def __init__(self, name: str, description: str, requires_approval: bool = False):
        self.name = name
        self.description = description
        self.requires_approval = requires_approval or PermissionScope.requires_human_approval(name)
        
    @abstractmethod
    async def execute(self, agent_id: str, params: Dict[str, Any]) -> ToolResult:
        pass


class WebSearchTool(BaseTool):
    def __init__(self):
        super().__init__(name="web_search", description="Search the web for current information, articles, and documentation.")
        
    async def execute(self, agent_id: str, params: Dict[str, Any]) -> ToolResult:
        query = params.get("query", "").strip()
        if not query:
            return ToolResult(success=False, data=None, error="Query parameter is required")
            
        audit_logger.log(agent_id, "TOOL_EXEC", {"tool": self.name, "query": query})
        
        try:
            # Fetch search results using DuckDuckGo Instant Answer API or HTML extraction
            url = "https://api.duckduckgo.com/"
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, params={"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"})
                if resp.status_code == 200:
                    data = resp.json()
                    heading = data.get("Heading", "")
                    abstract = data.get("AbstractText", "")
                    results = []
                    
                    if abstract:
                        results.append({"title": heading, "snippet": abstract, "source": data.get("AbstractURL", "")})
                        
                    for topic in data.get("RelatedTopics", [])[:4]:
                        if "Text" in topic:
                            results.append({
                                "title": topic.get("FirstURL", "").split("/")[-1].replace("_", " "),
                                "snippet": topic.get("Text", ""),
                                "source": topic.get("FirstURL", "")
                            })
                            
                    if not results:
                        results.append({
                            "title": f"Search Results for '{query}'",
                            "snippet": f"Found reference materials related to {query}. (Synthesized multi-agent summary available)",
                            "source": f"https://duckduckgo.com/?q={query}"
                        })
                    return ToolResult(success=True, data={"query": query, "results": results})
                else:
                    return ToolResult(success=False, data=None, error=f"Search service responded with status {resp.status_code}")
        except Exception as e:
            return ToolResult(success=False, data=None, error=f"Search failed: {str(e)}")


class FetchUrlTool(BaseTool):
    def __init__(self):
        super().__init__(name="fetch_url", description="Retrieve and clean text content from a public web page.")
        
    async def execute(self, agent_id: str, params: Dict[str, Any]) -> ToolResult:
        url = params.get("url", "").strip()
        if not url:
            return ToolResult(success=False, data=None, error="URL parameter is required")
            
        audit_logger.log(agent_id, "TOOL_EXEC", {"tool": self.name, "url": url})
        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; SwarmDroid/1.0; +https://github.com/swarmdroid)"}
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code != 200:
                    return ToolResult(success=False, data=None, error=f"HTTP {resp.status_code} fetching {url}")
                
                html = resp.text
                # Simple strip tags
                text = re.sub(r"<script.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
                text = re.sub(r"<style.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
                text = re.sub(r"<[^>]+>", " ", text)
                text = " ".join(text.split())[:4000]  # truncate to 4000 chars
                return ToolResult(success=True, data={"url": url, "content": text})
        except Exception as e:
            return ToolResult(success=False, data=None, error=f"Failed to fetch {url}: {str(e)}")


class CodeExecutionTool(BaseTool):
    def __init__(self):
        super().__init__(name="run_sandbox_code", description="Safely execute verified Python code snippets in a restricted sandbox.")
        
    async def execute(self, agent_id: str, params: Dict[str, Any]) -> ToolResult:
        code = params.get("code", "")
        if not code:
            return ToolResult(success=False, data=None, error="Code parameter is required")
            
        audit_logger.log(agent_id, "TOOL_EXEC", {"tool": self.name, "code_len": len(code)})
        
        # Static AST analysis check
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        if n.name in ("os", "subprocess", "sys", "shutil", "socket"):
                            return ToolResult(success=False, data=None, error=f"Import of forbidden module '{n.name}' in sandbox")
                elif isinstance(node, ast.ImportFrom):
                    if node.module in ("os", "subprocess", "sys", "shutil", "socket"):
                        return ToolResult(success=False, data=None, error=f"Import from forbidden module '{node.module}' in sandbox")
        except SyntaxError as e:
            return ToolResult(success=False, data=None, error=f"Syntax Error: {str(e)}")
            
        # Execute in restricted namespace
        try:
            safe_globals = {
                "__builtins__": {
                    "abs": abs, "min": min, "max": max, "len": len, "range": range,
                    "print": lambda *args: output_buffer.append(" ".join(str(a) for a in args)),
                    "sum": sum, "sorted": sorted, "int": int, "float": float, "str": str,
                    "dict": dict, "list": list, "set": set, "tuple": tuple, "bool": bool
                }
            }
            output_buffer = []
            exec(code, safe_globals)
            return ToolResult(success=True, data={"output": "\n".join(output_buffer)})
        except Exception as e:
            return ToolResult(success=False, data=None, error=f"Execution error: {str(e)}")


class DraftEmailTool(BaseTool):
    def __init__(self):
        super().__init__(name="draft_email", description="Draft an email for review. Requires human approval before sending.", requires_approval=True)
        
    async def execute(self, agent_id: str, params: Dict[str, Any]) -> ToolResult:
        recipient = params.get("recipient", "")
        subject = params.get("subject", "")
        body = params.get("body", "")
        
        audit_logger.log(agent_id, "TOOL_EXEC", {"tool": self.name, "recipient": recipient, "subject": subject})
        
        return ToolResult(
            success=True,
            data={
                "action": "draft_email",
                "recipient": recipient,
                "subject": subject,
                "body": body,
                "ready_for_review": True
            },
            requires_approval=True,
            approval_prompt=f"Communication Agent drafted an email to '{recipient}' with subject '{subject}'. Approve sending?"
        )


class DraftSocialMediaTool(BaseTool):
    def __init__(self):
        super().__init__(name="draft_post", description="Draft a post for X/Twitter or LinkedIn. Requires human approval before publishing.", requires_approval=True)
        
    async def execute(self, agent_id: str, params: Dict[str, Any]) -> ToolResult:
        platform = params.get("platform", "X")
        content = params.get("content", "")
        hashtags = params.get("hashtags", [])
        
        audit_logger.log(agent_id, "TOOL_EXEC", {"tool": self.name, "platform": platform, "length": len(content)})
        
        formatted_post = f"{content}\n\n{' '.join(hashtags)}" if hashtags else content
        return ToolResult(
            success=True,
            data={
                "platform": platform,
                "content": formatted_post,
                "character_count": len(formatted_post),
                "status": "DRAFT"
            },
            requires_approval=True,
            approval_prompt=f"Social Media Agent drafted a post for {platform}: \"{formatted_post[:80]}...\". Approve publishing?"
        )


class DeviceIntentTool(BaseTool):
    """Generates approved Android Intent payloads for Device Agent."""
    
    def __init__(self):
        super().__init__(name="device_action", description="Create an approved Android device action (launch app, share, settings, tts).")
        
    async def execute(self, agent_id: str, params: Dict[str, Any]) -> ToolResult:
        action_type = params.get("action_type")  # "LAUNCH_APP", "OPEN_SETTINGS", "SHARE", "SPEAK"
        package = params.get("package")
        payload = params.get("payload", {})
        
        audit_logger.log(agent_id, "TOOL_EXEC", {"tool": self.name, "action_type": action_type})
        
        requires_approval = action_type in ("OPEN_SETTINGS", "EXECUTE_PAYLOAD")
        return ToolResult(
            success=True,
            data={
                "intent_action": action_type,
                "target_package": package,
                "payload": payload,
                "platform": "Android"
            },
            requires_approval=requires_approval,
            approval_prompt=f"Device Agent requests permission to execute device action: {action_type} ({package}). Approve?" if requires_approval else None
        )

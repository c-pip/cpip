"""
Security module for SwarmDroid
- Prompt injection and jailbreak defense
- Tool allowlists & permission boundaries
- Sensitive secret & PII redaction
- Structured audit logger
"""

import re
import time
import uuid
from typing import List, Dict, Any, Optional, Set
from pydantic import BaseModel, Field


class SecurityEvaluation(BaseModel):
    is_safe: bool
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    flagged_reasons: List[str] = Field(default_factory=list)
    sanitized_input: str


class PromptDefense:
    """Scans user queries and agent inputs for prompt injection and malicious behavior."""
    
    # Common injection & exfiltration patterns
    INJECTION_PATTERNS = [
        (r"(?i)ignore\s+(all\s+)?(previous|prior)\s+(instructions|directives|prompts)", "Instruction override attempt"),
        (r"(?i)system\s*prompt\s*(leak|print|show|reveal|display|output)", "System prompt exfiltration attempt"),
        (r"(?i)you\s+are\s+now\s+(DAN|unfiltered|jailbroken|an\s+evil|developer\s+mode)", "Persona hijack / jailbreak attempt"),
        (r"(?i)sudo\s+rm\s+-rf", "Destructive command execution attempt"),
        (r"(?i)drop\s+table|delete\s+from\s+sqlite_master", "SQL injection attempt"),
        (r"(?i)bypass\s+(security|sandbox|policy|permissions)", "Security bypass attempt"),
        (r"(?i)format\s+(c:|root|\/dev\/sda)", "Filesystem destruction attempt"),
        (r"(?i)reveal\s+(api\s*key|secret|password|private\s*key)", "Credential exfiltration attempt")
    ]
    
    @classmethod
    def evaluate(cls, text: str) -> SecurityEvaluation:
        flags = []
        highest_risk = "LOW"
        
        for pattern, reason in cls.INJECTION_PATTERNS:
            if re.search(pattern, text):
                flags.append(reason)
                highest_risk = "HIGH" if "jailbreak" in reason or "override" in reason else "CRITICAL"
        
        is_safe = len(flags) == 0
        return SecurityEvaluation(
            is_safe=is_safe,
            risk_level=highest_risk if flags else "LOW",
            flagged_reasons=flags,
            sanitized_input=cls.sanitize(text)
        )
    
    @classmethod
    def sanitize(cls, text: str) -> str:
        # Strip potential null bytes and excessive control characters
        cleaned = text.replace("\x00", "").strip()
        return cleaned


class SecretRedactor:
    """Scans logs, thoughts, and agent outputs to redact sensitive credentials."""
    
    SECRET_PATTERNS = [
        (r"sk-[a-zA-Z0-9_-]{20,}", "[REDACTED_API_KEY]"),
        (r"AIzaSy[a-zA-Z0-9_-]{33}", "[REDACTED_GEMINI_KEY]"),
        (r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,32}", "[REDACTED_SLACK_TOKEN]"),
        (r"ghp_[a-zA-Z0-9]{36}", "[REDACTED_GITHUB_TOKEN]"),
        (r"Bearer\s+[a-zA-Z0-9_\-\.]{20,}", "Bearer [REDACTED_TOKEN]"),
        (r"(?i)(password|secret|apikey|api_key)\s*[:=]\s*['\"][^'\"]+['\"]", r"\1: '[REDACTED]'")
    ]
    
    @classmethod
    def redact(cls, text: str) -> str:
        if not text:
            return ""
        result = text
        for pattern, replacement in cls.SECRET_PATTERNS:
            result = re.sub(pattern, replacement, result)
        return result


class PermissionScope:
    """Defines which tools and operations an agent is authorized to use."""
    
    # Sensitive tools that strictly require Human-in-the-Loop user approval
    SENSITIVE_ACTIONS: Set[str] = {
        "send_email",
        "post_tweet",
        "post_social_media",
        "delete_memory",
        "modify_device_settings",
        "launch_sensitive_app",
        "execute_system_command",
        "write_external_file"
    }
    
    # Default tool allowances per agent role
    DEFAULT_ROLE_TOOLS: Dict[str, Set[str]] = {
        "MasterAgent": {"*"},  # Can delegate, not direct execute
        "BrowserAgent": {"web_search", "fetch_url", "extract_page_content"},
        "CommunicationAgent": {"draft_email", "send_email", "format_message", "draft_reply"},
        "CodingAgent": {"analyze_code", "generate_code", "run_sandbox_code", "lint_code"},
        "SocialMediaAgent": {"draft_post", "post_social_media", "create_content_calendar"},
        "DeviceAgent": {"launch_app", "get_device_status", "modify_device_settings", "share_text"},
        "ResearchAgent": {"web_search", "synthesize_sources", "fact_check", "extract_citations"},
        "MemoryAgent": {"search_memory", "store_memory", "delete_memory", "list_memories"},
        "SecurityAgent": {"evaluate_prompt", "audit_action", "verify_permissions"}
    }
    
    @classmethod
    def is_tool_allowed(cls, role: str, tool_name: str, custom_allowed_tools: Optional[Set[str]] = None) -> bool:
        if custom_allowed_tools is not None:
            return tool_name in custom_allowed_tools or "*" in custom_allowed_tools
        allowed = cls.DEFAULT_ROLE_TOOLS.get(role, set())
        return "*" in allowed or tool_name in allowed
    
    @classmethod
    def requires_human_approval(cls, tool_name: str) -> bool:
        return tool_name in cls.SENSITIVE_ACTIONS


class AuditLogEntry(BaseModel):
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = Field(default_factory=time.time)
    agent_id: str
    action_type: str  # "PROMPT_EVAL", "TOOL_EXEC", "APPROVAL_REQ", "APPROVAL_DECISION", "SECURITY_ALERT"
    details: Dict[str, Any] = Field(default_factory=dict)
    status: str = "SUCCESS"  # "SUCCESS", "BLOCKED", "PENDING_APPROVAL", "REJECTED"


class AuditLogger:
    """Maintains an append-only in-memory and persistence-ready security audit log."""
    
    def __init__(self):
        self._logs: List[AuditLogEntry] = []
    
    def log(self, agent_id: str, action_type: str, details: Dict[str, Any], status: str = "SUCCESS") -> AuditLogEntry:
        # Sanitize details before logging
        safe_details = {k: SecretRedactor.redact(str(v)) if isinstance(v, str) else v for k, v in details.items()}
        entry = AuditLogEntry(
            agent_id=agent_id,
            action_type=action_type,
            details=safe_details,
            status=status
        )
        self._logs.append(entry)
        return entry
    
    def get_recent(self, limit: int = 50) -> List[AuditLogEntry]:
        return self._logs[-limit:]


# Global audit logger instance
audit_logger = AuditLogger()

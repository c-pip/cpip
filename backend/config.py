"""
SwarmDroid Backend Configuration
"""

import os
from typing import Dict, Any
from pydantic import BaseModel, Field


class ProviderConfig(BaseModel):
    name: str
    api_key: str = ""
    base_url: str = ""
    default_model: str = ""
    enabled: bool = True


class SwarmConfig(BaseModel):
    # Server settings
    host: str = os.getenv("SWARMDROID_HOST", "0.0.0.0")
    port: int = int(os.getenv("SWARMDROID_PORT", "8000"))
    environment: str = os.getenv("SWARMDROID_ENV", "development")
    log_level: str = os.getenv("SWARMDROID_LOG_LEVEL", "INFO")
    
    # Concurrency and safety limits
    max_concurrent_tasks: int = int(os.getenv("MAX_CONCURRENT_TASKS", "6"))
    max_agent_depth: int = int(os.getenv("MAX_AGENT_DEPTH", "4"))
    task_timeout_seconds: float = float(os.getenv("TASK_TIMEOUT_SECONDS", "60.0"))
    max_task_retries: int = int(os.getenv("MAX_TASK_RETRIES", "2"))
    
    # Model providers
    default_provider: str = os.getenv("DEFAULT_AI_PROVIDER", "gemini")
    
    providers: Dict[str, ProviderConfig] = Field(default_factory=lambda: {
        "gemini": ProviderConfig(
            name="Google Gemini",
            api_key=os.getenv("GEMINI_API_KEY", ""),
            base_url="https://generativelanguage.googleapis.com/v1beta",
            default_model="gemini-2.0-flash",
            enabled=True
        ),
        "openai": ProviderConfig(
            name="OpenAI",
            api_key=os.getenv("OPENAI_API_KEY", ""),
            base_url="https://api.openai.com/v1",
            default_model="gpt-4o",
            enabled=True
        ),
        "anthropic": ProviderConfig(
            name="Anthropic Claude",
            api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            base_url="https://api.anthropic.com/v1",
            default_model="claude-3-5-sonnet-20241022",
            enabled=True
        ),
        "ollama": ProviderConfig(
            name="Ollama (Local)",
            api_key="",
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            default_model="llama3.2",
            enabled=True
        ),
        "openrouter": ProviderConfig(
            name="OpenRouter",
            api_key=os.getenv("OPENROUTER_API_KEY", ""),
            base_url="https://openrouter.ai/api/v1",
            default_model="google/gemini-2.0-flash-exp:free",
            enabled=True
        ),
        "custom": ProviderConfig(
            name="Custom OpenAI-compatible",
            api_key=os.getenv("CUSTOM_API_KEY", ""),
            base_url=os.getenv("CUSTOM_BASE_URL", "http://localhost:8080/v1"),
            default_model="default",
            enabled=False
        )
    })
    
    # Security and Storage
    memory_db_path: str = os.getenv("MEMORY_DB_PATH", "swarmdroid_memory.db")
    require_approval_for_sensitive: bool = True
    sanitize_inputs: bool = True


# Singleton config instance
settings = SwarmConfig()

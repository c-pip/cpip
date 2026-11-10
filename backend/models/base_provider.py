"""
Base LLM Provider Interface for SwarmDroid
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
from pydantic import BaseModel, Field


class LLMMessage(BaseModel):
    role: str  # "system", "user", "assistant"
    content: str


class LLMResponse(BaseModel):
    content: str
    model: str
    provider: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    finish_reason: str = "stop"
    raw_response: Optional[Dict[str, Any]] = None


class BaseLLMProvider(ABC):
    def __init__(self, api_key: str = "", base_url: str = "", default_model: str = ""):
        self.api_key = api_key
        self.base_url = base_url
        self.default_model = default_model
    
    @abstractmethod
    async def generate(self, messages: List[LLMMessage], model: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 2048) -> LLMResponse:
        """Generate a complete text response given a list of messages."""
        pass
    
    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """Test whether the provider API is accessible with the current configuration."""
        pass

"""
Concrete LLM Providers for SwarmDroid
- OpenAI & Compatible (OpenRouter, Custom)
- Google Gemini
- Anthropic Claude
- Ollama Local
"""

import httpx
from typing import List, Dict, Any, Optional
from .base_provider import BaseLLMProvider, LLMMessage, LLMResponse


class OpenAICompatibleProvider(BaseLLMProvider):
    """Supports OpenAI, OpenRouter, and any OpenAI-compatible API endpoint."""
    
    def __init__(self, api_key: str = "", base_url: str = "https://api.openai.com/v1", default_model: str = "gpt-4o", provider_name: str = "openai"):
        super().__init__(api_key=api_key, base_url=base_url, default_model=default_model)
        self.provider_name = provider_name
    
    async def generate(self, messages: List[LLMMessage], model: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 2048) -> LLMResponse:
        if not self.api_key and self.provider_name in ("openai", "anthropic", "openrouter"):
            raise ValueError(f"Missing API key for provider '{self.provider_name}'. Please configure your key in Model Settings.")
        
        target_model = model or self.default_model
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }
        if self.provider_name == "openrouter":
            headers["HTTP-Referer"] = "https://github.com/swarmdroid"
            headers["X-Title"] = "SwarmDroid AI"
            
        payload = {
            "model": target_model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"API Error ({self.provider_name} HTTP {resp.status_code}): {resp.text}")
            
            data = resp.json()
            choice = data["choices"][0]
            usage = data.get("usage", {})
            return LLMResponse(
                content=choice["message"]["content"] or "",
                model=target_model,
                provider=self.provider_name,
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                finish_reason=choice.get("finish_reason", "stop"),
                raw_response=data
            )
            
    async def test_connection(self) -> Dict[str, Any]:
        try:
            res = await self.generate(
                messages=[LLMMessage(role="user", content="Ping. Reply with 'Pong'.")],
                max_tokens=10
            )
            return {"status": "success", "provider": self.provider_name, "model": res.model, "reply": res.content.strip()}
        except Exception as e:
            return {"status": "error", "provider": self.provider_name, "error": str(e)}


class GeminiProvider(BaseLLMProvider):
    """Google Gemini native REST API."""
    
    def __init__(self, api_key: str = "", base_url: str = "https://generativelanguage.googleapis.com/v1beta", default_model: str = "gemini-2.0-flash"):
        super().__init__(api_key=api_key, base_url=base_url, default_model=default_model)
        self.provider_name = "gemini"
        
    async def generate(self, messages: List[LLMMessage], model: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 2048) -> LLMResponse:
        if not self.api_key:
            raise ValueError("Missing Gemini API key. Please configure your key in Model Settings.")
        
        target_model = model or self.default_model
        # Format for Gemini generateContent
        contents = []
        system_instruction = None
        
        for m in messages:
            if m.role == "system":
                system_instruction = {"parts": [{"text": m.content}]}
            else:
                role = "user" if m.role == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": m.content}]
                })
        
        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        if system_instruction:
            payload["systemInstruction"] = system_instruction
            
        url = f"{self.base_url.rstrip('/')}/models/{target_model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini API Error (HTTP {resp.status_code}): {resp.text}")
            
            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise RuntimeError("No candidate response returned from Gemini API")
            
            candidate = candidates[0]
            parts = candidate.get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts)
            usage = data.get("usageMetadata", {})
            
            return LLMResponse(
                content=text,
                model=target_model,
                provider="gemini",
                prompt_tokens=usage.get("promptTokenCount", 0),
                completion_tokens=usage.get("candidatesTokenCount", 0),
                finish_reason=candidate.get("finishReason", "STOP"),
                raw_response=data
            )
            
    async def test_connection(self) -> Dict[str, Any]:
        try:
            res = await self.generate(
                messages=[LLMMessage(role="user", content="Ping. Respond with 'Pong'.")],
                max_tokens=10
            )
            return {"status": "success", "provider": "gemini", "model": res.model, "reply": res.content.strip()}
        except Exception as e:
            return {"status": "error", "provider": "gemini", "error": str(e)}


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude Messages API."""
    
    def __init__(self, api_key: str = "", base_url: str = "https://api.anthropic.com/v1", default_model: str = "claude-3-5-sonnet-20241022"):
        super().__init__(api_key=api_key, base_url=base_url, default_model=default_model)
        self.provider_name = "anthropic"
        
    async def generate(self, messages: List[LLMMessage], model: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 2048) -> LLMResponse:
        if not self.api_key:
            raise ValueError("Missing Anthropic API key. Please configure your key in Model Settings.")
        
        target_model = model or self.default_model
        system_prompt = ""
        user_assistant_msgs = []
        for m in messages:
            if m.role == "system":
                system_prompt = m.content
            else:
                user_assistant_msgs.append({"role": m.role, "content": m.content})
                
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        payload = {
            "model": target_model,
            "messages": user_assistant_msgs,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        if system_prompt:
            payload["system"] = system_prompt
            
        url = f"{self.base_url.rstrip('/')}/messages"
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Anthropic API Error (HTTP {resp.status_code}): {resp.text}")
            
            data = resp.json()
            content_blocks = data.get("content", [])
            text = "".join(b.get("text", "") for b in content_blocks if b.get("type") == "text")
            usage = data.get("usage", {})
            return LLMResponse(
                content=text,
                model=target_model,
                provider="anthropic",
                prompt_tokens=usage.get("input_tokens", 0),
                completion_tokens=usage.get("output_tokens", 0),
                finish_reason=data.get("stop_reason", "end_turn"),
                raw_response=data
            )
            
    async def test_connection(self) -> Dict[str, Any]:
        try:
            res = await self.generate(
                messages=[LLMMessage(role="user", content="Ping. Respond with 'Pong'.")],
                max_tokens=10
            )
            return {"status": "success", "provider": "anthropic", "model": res.model, "reply": res.content.strip()}
        except Exception as e:
            return {"status": "error", "provider": "anthropic", "error": str(e)}


class OllamaProvider(BaseLLMProvider):
    """Local Ollama instance."""
    
    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "llama3.2"):
        super().__init__(api_key="", base_url=base_url, default_model=default_model)
        self.provider_name = "ollama"
        
    async def generate(self, messages: List[LLMMessage], model: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 2048) -> LLMResponse:
        target_model = model or self.default_model
        payload = {
            "model": target_model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens}
        }
        url = f"{self.base_url.rstrip('/')}/api/chat"
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Ollama Error (HTTP {resp.status_code}): {resp.text}")
            
            data = resp.json()
            return LLMResponse(
                content=data.get("message", {}).get("content", ""),
                model=target_model,
                provider="ollama",
                prompt_tokens=data.get("prompt_eval_count", 0),
                completion_tokens=data.get("eval_count", 0),
                finish_reason="stop",
                raw_response=data
            )
            
    async def test_connection(self) -> Dict[str, Any]:
        try:
            url = f"{self.base_url.rstrip('/')}/api/tags"
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    models = [m.get("name") for m in resp.json().get("models", [])]
                    return {"status": "success", "provider": "ollama", "models_available": models}
                return {"status": "error", "provider": "ollama", "error": resp.text}
        except Exception as e:
            return {"status": "error", "provider": "ollama", "error": str(e)}

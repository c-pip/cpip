"""
Provider Factory & Manager for SwarmDroid
Manages API keys, active providers, and fallback mechanisms.
"""

from typing import Dict, Any, Optional
from ..config import settings, ProviderConfig
from .base_provider import BaseLLMProvider
from .providers import OpenAICompatibleProvider, GeminiProvider, AnthropicProvider, OllamaProvider


class ProviderManager:
    def __init__(self):
        self._providers: Dict[str, BaseLLMProvider] = {}
        self._init_providers()
        
    def _init_providers(self):
        for name, cfg in settings.providers.items():
            self._providers[name] = self._create_provider_instance(name, cfg)
            
    def _create_provider_instance(self, name: str, cfg: ProviderConfig) -> BaseLLMProvider:
        if name == "gemini":
            return GeminiProvider(api_key=cfg.api_key, base_url=cfg.base_url, default_model=cfg.default_model)
        elif name == "anthropic":
            return AnthropicProvider(api_key=cfg.api_key, base_url=cfg.base_url, default_model=cfg.default_model)
        elif name == "ollama":
            return OllamaProvider(base_url=cfg.base_url, default_model=cfg.default_model)
        elif name in ("openai", "openrouter", "custom"):
            return OpenAICompatibleProvider(
                api_key=cfg.api_key,
                base_url=cfg.base_url,
                default_model=cfg.default_model,
                provider_name=name
            )
        else:
            return OpenAICompatibleProvider(api_key=cfg.api_key, base_url=cfg.base_url, default_model=cfg.default_model, provider_name=name)

    def set_api_key(self, provider_name: str, api_key: str):
        if provider_name in settings.providers:
            settings.providers[provider_name].api_key = api_key
            self._providers[provider_name] = self._create_provider_instance(
                provider_name, settings.providers[provider_name]
            )
            
    def configure_provider(self, provider_name: str, config: Dict[str, Any]):
        if provider_name not in settings.providers:
            settings.providers[provider_name] = ProviderConfig(name=provider_name)
        cfg = settings.providers[provider_name]
        if "api_key" in config:
            cfg.api_key = config["api_key"]
        if "base_url" in config:
            cfg.base_url = config["base_url"]
        if "default_model" in config:
            cfg.default_model = config["default_model"]
        if "enabled" in config:
            cfg.enabled = bool(config["enabled"])
            
        self._providers[provider_name] = self._create_provider_instance(provider_name, cfg)

    def get_provider(self, provider_name: Optional[str] = None) -> BaseLLMProvider:
        target = provider_name or settings.default_provider
        if target not in self._providers:
            # Fallback to gemini or openai if available
            target = "gemini" if "gemini" in self._providers else list(self._providers.keys())[0]
        return self._providers[target]

    async def test_all(self) -> Dict[str, Any]:
        results = {}
        for name, prov in self._providers.items():
            results[name] = await prov.test_connection()
        return results

    def list_status(self) -> Dict[str, Any]:
        status = {}
        for name, cfg in settings.providers.items():
            status[name] = {
                "name": cfg.name,
                "enabled": cfg.enabled,
                "has_key": bool(cfg.api_key),
                "base_url": cfg.base_url,
                "default_model": cfg.default_model
            }
        return status


# Global provider manager instance
provider_manager = ProviderManager()

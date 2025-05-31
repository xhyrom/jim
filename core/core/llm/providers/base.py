from abc import ABC, abstractmethod
from typing import Any, Dict, List


class LLMProvider(ABC):
    """Base class for LLM providers"""

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate a response from the LLM"""
        pass


class ProviderRegistry:
    _providers = {}

    @classmethod
    def register(cls, name):
        """Register an LLM provider implementation"""

        def decorator(provider_class):
            cls._providers[name] = provider_class
            return provider_class

        return decorator

    @classmethod
    def get_provider(cls, name, **kwargs):
        """Get a provider by name"""
        provider_class = cls._providers.get(name)
        if provider_class:
            return provider_class(**kwargs)
        raise ValueError(f"Unknown LLM provider: {name}")

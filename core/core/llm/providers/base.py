from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


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
        
    async def complete(
        self,
        text: str,
        conversation_history: List[Dict[str, str]] = None,
        contexts: List[str] = None,
        stream: bool = False,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs,
    ) -> Dict[str, Any]:
        """Complete the given text using the LLM.
        
        This is a higher-level method that formats the inputs into the expected format
        and calls generate_response.
        
        Args:
            text: The text input from the user
            conversation_history: Previous messages in the conversation
            contexts: Additional context information
            stream: Whether to stream the response
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature parameter for response generation
            
        Returns:
            Dict with response and other metadata
        """
        if conversation_history is None:
            conversation_history = []
            
        # Format messages for the provider
        messages = list(conversation_history)  # Make a copy
        
        # Add the current user message
        messages.append({"role": "user", "content": text})
        
        # Add contexts if provided (as system messages at the beginning)
        if contexts and len(contexts) > 0:
            context_content = "\n".join(contexts)
            # Check if we already have a system message
            has_system = any(msg["role"] == "system" for msg in messages)
            
            if has_system:
                # Find and update the existing system message
                for msg in messages:
                    if msg["role"] == "system":
                        msg["content"] = f"{msg['content']}\n{context_content}"
                        break
            else:
                # Insert a new system message at the beginning
                messages.insert(0, {"role": "system", "content": context_content})
        
        # Call the provider-specific implementation
        response_data = await self.generate_response(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream,
            **kwargs
        )
        
        # Format the response for the client
        content = response_data.get("content", "")
        
        return {
            "response": content,
            "success": True,
            "provider": response_data.get("provider", "unknown"),
            "model": response_data.get("model", "unknown"),
            "finish_reason": response_data.get("finish_reason", "unknown"),
            "raw_response": response_data,
        }


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
    
    @classmethod
    def list_providers(cls):
        """Get a list of all registered provider names"""
        return list(cls._providers.keys())

import random
from typing import Any, Dict, List

from .base import LLMProvider, ProviderRegistry


@ProviderRegistry.register("mock")
class MockProvider(LLMProvider):
    """Mock LLM provider for testing"""

    def __init__(self, **kwargs):
        self.responses = [
            "I'll help you with that.",
            "I'm not sure I understand, could you rephrase?",
            "Here's what I found for you.",
            "That's an interesting question.",
            "I don't have specific information on that topic.",
        ]
        self.max_tokens = kwargs.get("max_tokens", 50)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate a mock response"""

        user_message = next((m["content"] for m in messages if m["role"] == "user"), "")

        max_len = min(self.max_tokens, max_tokens)

        response = random.choice(self.responses)
        if user_message:
            response += f" Regarding '{user_message}...'"

        return {
            "content": response[:max_len],
            "finish_reason": "stop",
            "model": "mock-model",
            "provider": "mock",
        }

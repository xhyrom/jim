from typing import Any, Dict, List

from openai import AsyncOpenAI

from .base import LLMProvider, ProviderRegistry


@ProviderRegistry.register("openai")
class OpenAIProvider(LLMProvider):
    def __init__(self, **kwargs):
        self.api_key = kwargs.get("api_key", "")
        self.model = kwargs.get("model", "gpt-3.5-turbo")
        self.base_url = kwargs.get("base_url", "https://api.openai.com/v1")

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url if kwargs.get("base_url") else None,
        )

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs,
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            return {
                "content": response.choices[0].message.content,
                "finish_reason": response.choices[0].finish_reason,
                "model": response.model,
                "provider": "openai",
            }
        except Exception as e:
            print(f"Error generating response from OpenAI: {e}")
            return {
                "content": "I apologize, but I'm having trouble processing your request at the moment.",
                "finish_reason": "error",
                "model": self.model,
                "provider": "openai",
                "error": str(e),
            }

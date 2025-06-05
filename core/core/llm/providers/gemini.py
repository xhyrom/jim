from typing import Any, Dict, List

from google import genai
from google.genai import types

from ...skills.weather.handler import get_weather_by_location
from .base import LLMProvider, ProviderRegistry


@ProviderRegistry.register("gemini")
class GeminiProvider(LLMProvider):
    """Google Gemini API provider using the official client library"""

    def __init__(self, **kwargs):
        self.api_key = kwargs.get("api_key", "")
        self.model = kwargs.get("model", "gemini-2.5-flash")
        self.client = None

        if not self.api_key:
            print("Warning: Gemini API key not provided")
        else:
            self.client = genai.Client(api_key=self.api_key)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate a response using Google Gemini API"""

        if not self.api_key or not self.client:
            raise ValueError(
                "Gemini API key not provided or client initialization failed"
            )

        try:
            system_instruction = None
            contents = []

            for msg in messages:
                if msg["role"] == "system":
                    system_instruction = msg["content"]
                elif msg["role"] == "user":
                    contents.append(
                        types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=msg["content"])],
                        )
                    )
                elif msg["role"] == "assistant":
                    contents.append(
                        types.Content(
                            role="model",
                            parts=[types.Part.from_text(text=msg["content"])],
                        )
                    )

            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=0.95,
                top_k=40,
                tools=[get_weather_by_location],
            )

            if system_instruction:
                config.system_instruction = system_instruction

            response = await self.client.aio.models.generate_content(
                model=self.model, contents=contents, config=config
            )

            return {
                "content": response.text,
                "finish_reason": "stop",
                "model": self.model,
                "provider": "gemini",
            }

        except Exception as e:
            print(f"Error generating response from Gemini: {e}")
            return {
                "content": "I apologize, but I'm having trouble processing your request at the moment.",
                "finish_reason": "error",
                "model": self.model,
                "provider": "gemini",
                "error": str(e),
            }

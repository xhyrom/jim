from typing import Any, Dict, List

from google import genai

from .base import LLMProvider, ProviderRegistry


@ProviderRegistry.register("gemini")
class GeminiProvider(LLMProvider):
    """Google Gemini API provider using the official client library"""

    def __init__(self, **kwargs):
        self.api_key = kwargs.get("api_key", "")
        self.model = kwargs.get("model", "gemini-pro")

        if not self.api_key:
            print("Warning: Gemini API key not provided")
        else:
            genai.configure(api_key=self.api_key)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate a response using Google Gemini API"""
        if not self.api_key:
            raise ValueError("Gemini API key not provided")

        try:
            gemini_messages = []

            system_message = None
            for msg in messages:
                if msg["role"] == "user":
                    gemini_messages.append(
                        {"role": "user", "parts": [{"text": msg["content"]}]}
                    )
                elif msg["role"] == "assistant":
                    gemini_messages.append(
                        {"role": "model", "parts": [{"text": msg["content"]}]}
                    )
                elif msg["role"] == "system":
                    system_message = msg["content"]

            if system_message and gemini_messages:
                gemini_messages.insert(
                    0,
                    {
                        "role": "user",
                        "parts": [{"text": f"System instruction: {system_message}"}],
                    },
                )

            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "top_p": 0.95,
                "top_k": 40,
            }

            model = genai.GenerativeModel(
                model_name=self.model, generation_config=generation_config
            )

            chat = model.start_chat(history=gemini_messages)

            response = await chat.send_message_async("")

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

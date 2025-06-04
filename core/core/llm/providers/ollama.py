from typing import Any, Dict, List

import aiohttp

from .base import LLMProvider, ProviderRegistry


@ProviderRegistry.register("ollama")
class OllamaProvider(LLMProvider):
    def __init__(self, **kwargs):
        self.base_url = kwargs.get("base_url", "http://localhost:11434")
        self.model = kwargs.get("model", "llama3")

        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs,
    ) -> Dict[str, Any]:
        try:
            system_content = ""
            for msg in messages:
                if msg["role"] == "system":
                    system_content = msg["content"]
                    break

            formatted_messages = []
            for msg in messages:
                if msg["role"] != "system":
                    formatted_messages.append(
                        {"role": msg["role"], "content": msg["content"]}
                    )

            payload = {
                "model": self.model,
                "messages": formatted_messages,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }

            if system_content:
                payload["system"] = system_content

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ValueError(
                            f"Ollama API error: {response.status} - {error_text}"
                        )

                    data = await response.json()

                    return {
                        "content": data.get("message", {}).get("content", ""),
                        "finish_reason": "stop",
                        "model": self.model,
                        "provider": "ollama",
                    }

        except Exception as e:
            print(f"Error generating response from Ollama: {e}")
            return {
                "content": "I apologize, but I'm having trouble processing your request at the moment.",
                "finish_reason": "error",
                "model": self.model,
                "provider": "ollama",
                "error": str(e),
            }

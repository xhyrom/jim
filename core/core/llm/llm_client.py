from typing import Any, Dict, List, Optional

from ..config import LLMConfig
from .providers import get_provider


class LLMClient:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.provider = get_provider(config)
        self.conversation_history = {}

    async def get_response(
        self,
        text: str,
        user_id: str = "default",
        contexts: Optional[List[str]] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Get a response from the LLM."""

        if not self.config.enabled:
            return {
                "response": "LLM fallback is currently disabled.",
                "success": False,
            }

        try:
            history = self.get_conversation_history(user_id)

            all_contexts = self.config.contexts.copy()
            if contexts:
                all_contexts.extend(contexts)

            response = await self.provider.complete(
                text=text,
                conversation_history=history,
                contexts=all_contexts,
                stream=stream and self.config.streaming,
            )

            if response.get("success", False):
                self.add_to_conversation_history(
                    user_id=user_id,
                    user_message=text,
                    assistant_message=response.get("response", ""),
                )

            return response

        except Exception as e:
            print(f"LLM response error: {e}")

            return {
                "response": "I'm sorry, I had trouble processing that request.",
                "success": False,
                "error": str(e),
            }

    def get_conversation_history(
        self, user_id: str = "default"
    ) -> List[Dict[str, str]]:
        return self.conversation_history.get(user_id, [])

    def add_to_conversation_history(
        self, user_id: str, user_message: str, assistant_message: str
    ) -> None:
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []

        self.conversation_history[user_id].append(
            {"role": "user", "content": user_message}
        )
        self.conversation_history[user_id].append(
            {"role": "assistant", "content": assistant_message}
        )

        max_history = 10
        if len(self.conversation_history[user_id]) > max_history:
            self.conversation_history[user_id] = self.conversation_history[user_id][
                -max_history:
            ]

    def clear_conversation_history(self, user_id: str = "default") -> None:
        if user_id in self.conversation_history:
            self.conversation_history[user_id] = []

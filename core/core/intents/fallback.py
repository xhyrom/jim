from typing import Dict, Any


class FallbackHandler:
    def __init__(self):
        self.default_responses = [
            "I'm not sure I understand. Could you rephrase that?",
            "I don't know how to help with that yet.",
            "I didn't catch that. What would you like me to do?",
            "I'm not sure what you mean.",
        ]

        self.response_index = 0

    def handle_fallback(
        self, text: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        response = self.default_responses[self.response_index]
        self.response_index = (self.response_index + 1) % len(self.default_responses)

        return {"response": response, "action": None}

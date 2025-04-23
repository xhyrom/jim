from typing import Dict, Any, Callable


class IntentHandlerRegistry:
    handlers: Dict[str, Callable]

    def __init__(self):
        self.handlers = {}

    def register(self, intent_name: str, handler: Callable):
        self.handlers[intent_name] = handler

    def get_handler(self, intent_name: str) -> Callable | None:
        return self.handlers.get(intent_name)

    def execute(self, intent_name: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        handler = self.get_handler(intent_name)
        if handler:
            return handler(entities)
        return {"error": f"No handler found for intent {intent_name}"}

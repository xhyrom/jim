import importlib
import inspect
from pathlib import Path
from typing import Any, Callable, Dict, Optional


class HandlerRegistry:
    def __init__(self):
        self.handlers = {}
        self._load_default_handlers()

    def register(self, intent_name: str, handler_func: Callable):
        self.handlers[intent_name] = handler_func

    def get_handler(self, intent_name: str) -> Optional[Callable]:
        return self.handlers.get(intent_name)

    def _load_default_handlers(self):
        skills_dir = Path(__file__).parent.parent / "skills"

        if not skills_dir.exists():
            return

        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith("__"):
                continue

            try:
                module_name = f"core.skills.{skill_dir.name}.handler"
                handler_module = importlib.import_module(module_name)

                for name, func in inspect.getmembers(
                    handler_module, inspect.isfunction
                ):
                    if hasattr(func, "__doc__") and func.__doc__:
                        if "intent:" in func.__doc__:
                            intent_line = [
                                line
                                for line in func.__doc__.split("\n")
                                if "intent:" in line
                            ][0]
                            intent_name = intent_line.split("intent:")[1].strip()
                            self.register(intent_name, func)
                            print(f"Registered handler for intent: {intent_name}")
            except (ImportError, AttributeError) as e:
                print(f"Error loading handlers from {skill_dir.name}: {e}")

    async def process_intent(
        self, result: Dict[str, Any], user_id: str, device_id: str, config: Any
    ) -> Dict[str, Any]:
        intent_name = result.get("intent")
        confidence = result.get("confidence", 0.0)

        should_use_fallback = False
        if config.llm.enabled:
            if intent_name == "fallback" or confidence < config.llm.fallback_threshold:
                should_use_fallback = True

        if should_use_fallback:
            from ..skills.fallback import llm_fallback

            try:
                fallback_result = await llm_fallback(
                    entities=result.get("entities", {}),
                    user_id=user_id,
                    device_id=device_id,
                    config=config,
                    text=result.get("text", ""),
                    intent=intent_name,
                    confidence=confidence,
                )

                if "data" in fallback_result and "response" in fallback_result["data"]:
                    return {
                        "intent": "llm_fallback",
                        "confidence": 1.0,
                        "response": fallback_result["data"]["response"],
                        "action": fallback_result.get("action"),
                        "fallback_data": fallback_result.get("data", {}),
                    }
            except Exception as e:
                print(f"Error executing LLM fallback handler: {e}")

        handler = self.get_handler(intent_name)

        if not handler:
            return {
                "intent": intent_name,
                "confidence": result.get("confidence", 0.0),
                "response": "I understand, but I don't have a handler for that yet.",
            }

        try:
            entities = result.get("entities", {})

            handler_result = await handler(
                entities=entities, user_id=user_id, device_id=device_id, config=config
            )

            context = handler_result.get("data", {})

            response = result.get("echo").get_response(intent_name, context)

            return {
                "intent": intent_name,
                "confidence": result.get("confidence", 0.0),
                "response": response,
                "action": handler_result.get("action"),
            }

        except Exception as e:
            print(f"Error executing handler for intent {intent_name}: {e}")
            return {
                "intent": intent_name,
                "confidence": result.get("confidence", 0.0),
                "response": "I had trouble processing that request.",
                "error": str(e),
            }

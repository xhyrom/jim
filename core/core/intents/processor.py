from typing import Dict, Any, Optional, List
from .loader import IntentLoader
from .fallback import FallbackHandler
from .nlu import NLUEngine, PatternNLU


class IntentProcessor:
    def __init__(self, intent_loader: IntentLoader):
        self.intent_loader = intent_loader
        self.fallback_handler = FallbackHandler()
        self.nlu_engines = []

        pattern_nlu = PatternNLU()
        self._initialize_engine(pattern_nlu)
        self.nlu_engines.append(pattern_nlu)

    def _initialize_engine(self, engine: NLUEngine):
        engine.initialize(self.intent_loader.intents)

    def process(self, text: str, user_id: str, device_id: str) -> Dict[str, Any]:
        best_match = None
        best_confidence = -1.0

        for engine in self.nlu_engines:
            try:
                result = engine.parse(text)
                confidence = result.get("confidence", 0.0)

                if result.get("intent") and confidence > best_confidence:
                    best_match = result
                    best_confidence = confidence
            except Exception as e:
                print(f"Error processing with {type(engine).__name__}: {e}")

        if not best_match or not best_match.get("intent"):
            fallback_result = self.fallback_handler.handle_fallback(
                text, {"user_id": user_id, "device_id": device_id}
            )

            return {
                "intent": "unknown",
                "confidence": 0.0,
                "response": fallback_result.get(
                    "response", "I'm not sure what you mean."
                ),
                "action": fallback_result.get("action"),
            }

        intent_name = best_match["intent"]
        intent_entities = best_match.get("entities", {})
        intent_config = best_match.get("intent_config", {})

        intent_handler = self.intent_loader.handlers.get(intent_name)

        if intent_handler:
            try:
                result = intent_handler(
                    intent_entities, user_id=user_id, device_id=device_id
                )

                if isinstance(result, dict) and "response" in result:
                    return {
                        "intent": intent_name,
                        "confidence": best_match.get("confidence", 0.0),
                        "response": result["response"],
                        "action": result.get("action"),
                    }
            except Exception as e:
                print(f"Error executing handler for intent {intent_name}: {e}")

        return {
            "intent": intent_name,
            "confidence": best_match.get("confidence", 0.0),
            "response": "I understand, but I don't know how to handle that yet.",
        }

import re
from difflib import SequenceMatcher

from ..utils.regex import clean_pattern_for_fuzzy
from ..utils.text import normalize_text


class IntentMatcher:
    def __init__(self, intent_registry):
        self.intent_registry = intent_registry
        self.threshold = 0.6

    def match(self, text, entities=None):
        entities = entities or {}
        normalized_text = normalize_text(text)

        best_intent = None
        best_confidence = 0.0
        best_match = None

        for intent_name, intent_config in self.intent_registry.intents.items():
            patterns = intent_config.get("patterns", [])

            for pattern in patterns:
                processed_pattern = self._process_pattern(pattern, entities)

                match = re.match(
                    f"^{processed_pattern}$", normalized_text, re.IGNORECASE
                )
                if match:
                    confidence = 0.95

                    if confidence > best_confidence:
                        best_intent = intent_name
                        best_confidence = confidence
                        best_match = {"pattern": pattern, "match_obj": match}

        if best_confidence < self.threshold:
            for intent_name, intent_config in self.intent_registry.intents.items():
                patterns = intent_config.get("patterns", [])

                for pattern in patterns:
                    clean_pattern = clean_pattern_for_fuzzy(pattern)

                    ratio = SequenceMatcher(
                        None, clean_pattern, normalized_text
                    ).ratio()

                    if ratio > best_confidence:
                        best_intent = intent_name
                        best_confidence = ratio
                        best_match = {"pattern": pattern, "ratio": ratio}

        if best_confidence < self.threshold:
            return {"intent": "fallback", "confidence": 0.0, "match": None}

        return {
            "intent": best_intent,
            "confidence": best_confidence,
            "match": best_match,
        }

    def _process_pattern(self, pattern, entities):
        processed = pattern

        entity_placeholders = re.findall(r"\{(\w+)\}", pattern)

        for entity_name in entity_placeholders:
            if entity_name in entities:
                values = [e["raw_value"] for e in entities[entity_name]]
                if values:
                    for value in values:
                        processed = processed.replace(
                            f"{{{entity_name}}}", re.escape(value)
                        )
            else:
                processed = processed.replace(f"{{{entity_name}}}", r"[\w\s]+")

        return processed

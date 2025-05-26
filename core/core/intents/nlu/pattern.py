import re
from typing import Dict, Any

from . import NLUEngine


class PatternNLU(NLUEngine):
    def __init__(self):
        self.intent_patterns = {}
        self.intent_configs = {}

    def initialize(self, intents_data: Dict[str, Any]) -> None:
        for intent_name, intent_config in intents_data.items():
            patterns = intent_config.get("patterns", [])
            self.intent_patterns[intent_name] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
            self.intent_configs[intent_name] = intent_config

    def parse(self, text: str) -> Dict[str, Any]:
        for intent_name, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = pattern.match(text)
                if match:
                    entities = match.groupdict()
                    return {
                        "intent": intent_name,
                        "entities": entities,
                        "confidence": 0.9,
                        "intent_config": self.intent_configs[intent_name],
                    }

        return {"intent": None, "entities": {}, "confidence": 0.0}

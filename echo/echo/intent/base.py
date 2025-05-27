import re

from ..utils.regex import convert_entity_placeholders


class Intent:
    def __init__(self, name, config):
        self.name = name
        self.patterns = config.get("patterns", [])
        self.required_entities = config.get("requires", [])

        self.compiled_patterns = []
        for pattern in self.patterns:
            pattern = convert_entity_placeholders(pattern)
            self.compiled_patterns.append(re.compile(pattern, re.IGNORECASE))

    def matches(self, text, entities=None):
        entities = entities or {}

        for entity in self.required_entities:
            if entity not in entities:
                return False, 0.0

        for pattern in self.compiled_patterns:
            if pattern.match(text):
                return True, 0.9

        return False, 0.0

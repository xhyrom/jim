from typing import Any, Dict, List

from ..utils.text import extract_entity_placeholder


class EntityExtractor:
    def __init__(self, entity_registry):
        self.entity_registry = entity_registry

    def extract_from_pattern(self, text: str, pattern: str) -> Dict[str, List[Any]]:
        entity_names = extract_entity_placeholder(pattern)

        if not entity_names:
            return {}

        results = {}

        for entity_name in entity_names:
            entity_handler = self.entity_registry.get_entity(entity_name)
            if entity_handler:
                extracted = entity_handler.extract(text)
                if extracted:
                    results[entity_name] = extracted

        return results

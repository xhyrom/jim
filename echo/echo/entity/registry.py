from ..entity.standard import STANDARD_ENTITIES
from .base import Entity


class EntityRegistry:
    def __init__(self, config):
        self.config = config
        self.entities = {}

        self._register_entities()

    def _register_entities(self):
        for entity_name, entity_config in self.config.entities.items():
            try:
                entity_type = entity_config.get("type", entity_name)

                if entity_type in STANDARD_ENTITIES:
                    entity_class = STANDARD_ENTITIES[entity_type]
                    entity_handler = entity_class(entity_name, entity_config)
                else:
                    entity_handler = Entity(entity_name, entity_config)

                self.entities[entity_name] = entity_handler
            except Exception as e:
                print(f"Error registering entity {entity_name}: {e}")

    def register_entity(self, entity_name, entity_handler):
        self.entities[entity_name] = entity_handler

    def get_entity(self, entity_name):
        return self.entities.get(entity_name)

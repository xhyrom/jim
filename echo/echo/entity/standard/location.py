from ..base import Entity


class LocationEntity(Entity):
    def process_value(self, raw_value):
        # TODO: Implement more sophisticated location processing

        return {"name": raw_value, "type": "location"}

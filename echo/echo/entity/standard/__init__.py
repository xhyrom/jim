from .datetime import DateEntity, DurationEntity, TimeEntity
from .location import LocationEntity
from .numeric import NumberEntity
from .weather import (
    PrecipitationEntity,
    TemperatureEntity,
    WeatherConditionEntity,
    WindEntity,
)

STANDARD_ENTITIES = {
    "date": DateEntity,
    "time": TimeEntity,
    "duration": DurationEntity,
    "location": LocationEntity,
    "number": NumberEntity,
    "weather_condition": WeatherConditionEntity,
    "temperature": TemperatureEntity,
    "precipitation": PrecipitationEntity,
    "wind": WindEntity,
}

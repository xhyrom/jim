from typing import Any, Callable, Dict

from . import common, datetime, weather

MappingFunction = Callable[[Dict[str, Any]], str]

INTENT_MAPPINGS: Dict[str, MappingFunction] = {
    # Datetime intents
    "get_time": datetime.get_time_mapping,
    "get_date": datetime.get_date_mapping,
    # Weather intents
    "get_weather": weather.get_weather_mapping,
    "get_temperature": weather.get_temperature_mapping,
    "get_precipitation": weather.get_precipitation_mapping,
    "get_wind": weather.get_wind_mapping,
    # Common intents
    "greeting": common.greeting_mapping,
}


def get_response_key(intent_name: str, context: Dict[str, Any]) -> str:
    """Get the appropriate response key for an intent based on context."""

    if intent_name in INTENT_MAPPINGS:
        return INTENT_MAPPINGS[intent_name](context)

    return f"{intent_name}.default"

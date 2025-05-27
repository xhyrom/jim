from typing import Any, Dict


def get_weather_mapping(context: Dict[str, Any]) -> str:
    """Determine the appropriate response template for get_weather intent."""

    has_location = "location" in context and context["location"]
    has_date = "date" in context and context["date"]
    has_precipitation = "precipitation" in context and context["precipitation"]
    has_wind = "wind" in context and context["wind"]

    if has_precipitation and has_wind:
        return "get_weather.with_all"
    elif has_precipitation:
        return "get_weather.with_precipitation"
    elif has_wind:
        return "get_weather.with_wind"

    if has_location and has_date:
        return "get_weather.with_location_date"
    elif has_location:
        return "get_weather.with_location"
    elif has_date:
        return "get_weather.with_date"
    else:
        return "get_weather.default"


def get_temperature_mapping(context: Dict[str, Any]) -> str:
    """Determine the appropriate response template for get_temperature intent."""

    has_location = "location" in context and context["location"]
    has_date = "date" in context and context["date"]
    has_high_low = (
        "high_temperature" in context
        and context["high_temperature"]
        and "low_temperature" in context
        and context["low_temperature"]
    )

    if has_high_low:
        return "get_temperature.with_high_low"
    elif has_location and has_date:
        return "get_temperature.with_location_date"
    elif has_location:
        return "get_temperature.with_location"
    elif has_date:
        return "get_temperature.with_date"
    else:
        return "get_temperature.default"


def get_precipitation_mapping(context: Dict[str, Any]) -> str:
    """Determine the appropriate response template for get_precipitation intent."""

    has_location = "location" in context and context["location"]
    has_date = "date" in context and context["date"]
    is_umbrella_query = context.get("query_type") == "umbrella"
    precipitation_chance = context.get("precipitation_chance", 0)

    if is_umbrella_query:
        if precipitation_chance > 30:
            return "get_precipitation.with_umbrella_needed"
        else:
            return "get_precipitation.with_umbrella_not_needed"

    if has_location and has_date:
        return "get_precipitation.with_location_date"
    elif has_location:
        return "get_precipitation.with_location"
    elif has_date:
        return "get_precipitation.with_date"
    else:
        return "get_precipitation.default"


def get_wind_mapping(context: Dict[str, Any]) -> str:
    """Determine the appropriate response template for get_wind intent."""

    has_location = "location" in context and context["location"]
    has_date = "date" in context and context["date"]

    if has_location and has_date:
        return "get_wind.with_location_date"
    elif has_location:
        return "get_wind.with_location"
    elif has_date:
        return "get_wind.with_date"
    else:
        return "get_wind.default"

from typing import Any, Dict


def get_weather_mapping(context: Dict[str, Any]) -> str:
    """Determine the appropriate response template for get_weather intent."""

    has_location = "location" in context and context["location"]
    has_date = "date" in context and context["date"] != "today"
    has_precipitation = context.get("has_precipitation", False)
    has_wind = context.get("wind", "")

    if has_precipitation:
        if has_location:
            return "get_weather.with_precipitation_location"
        return "get_weather.with_precipitation"

    if "strong" in has_wind:
        if has_location:
            return "get_weather.with_strong_wind_location"
        return "get_weather.with_strong_wind"

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
    has_date = "date" in context and context["date"] != "today"
    has_feels_like = "feels_like" in context and context["feels_like"]

    if has_feels_like:
        if has_location:
            return "get_temperature.with_feels_like_location"
        return "get_temperature.with_feels_like"
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
    has_date = "date" in context and context["date"] != "today"
    has_precipitation = context.get("has_precipitation", False)

    if not has_precipitation:
        if has_location:
            return "get_precipitation.no_rain_location"
        return "get_precipitation.no_rain"

    if "umbrella" in context.get("text", "").lower():
        return "get_precipitation.with_umbrella"

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
    has_date = "date" in context and context["date"] != "today"

    if has_location and has_date:
        return "get_wind.with_location_date"
    elif has_location:
        return "get_wind.with_location"
    elif has_date:
        return "get_wind.with_date"
    else:
        return "get_wind.default"

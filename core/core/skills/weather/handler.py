from typing import Any, Dict, Optional
from datetime import datetime
import asyncio
from .services import WeatherServiceRegistry
from .geocoding import GeocodingService


async def get_weather_data(location_name: Optional[str], config: Any) -> Dict[str, Any]:
    """Get weather data for a location"""

    geocoding_config = config.geocoding
    geocoding_service = GeocodingService(
        base_url=geocoding_config.base_url, user_agent=geocoding_config.user_agent
    )

    location_data = None
    if location_name:
        location_data = await geocoding_service.geocode(location_name)

    if not location_data:
        location_data = await geocoding_service.get_location_from_ip()

    if not location_data:
        return {"success": False, "error": "Could not determine location"}

    location_name = location_data.get("city", "") or location_data.get("name", "")
    if "," in location_name:
        location_name = location_name.split(",")[0].strip()

    weather_config = config.weather
    weather_service = WeatherServiceRegistry.get_service(
        weather_config.implementation,
        api_key=weather_config.api_key,
        base_url=weather_config.base_url,
    )

    if not weather_service:
        return {
            "success": False,
            "error": f"Weather service '{weather_config.implementation}' not found",
            "location": location_name,
        }

    try:
        current_weather = await weather_service.get_current_weather(
            lat=location_data["lat"],
            lon=location_data["lon"],
            units=weather_config.units,
        )

        forecast = await weather_service.get_forecast(
            lat=location_data["lat"],
            lon=location_data["lon"],
            units=weather_config.units,
        )

        weather_condition = current_weather.get("weather_description", "unknown")
        humidity = current_weather.get("humidity", 0)
        wind_speed = current_weather.get("wind_speed", 0)
        temp = current_weather.get("temperature")
        feels_like = current_weather.get("feels_like")

        rain = current_weather.get("rain", 0)
        snow = current_weather.get("snow", 0)

        precipitation_status = "none"
        if rain > 0.5 or snow > 0.5:
            precipitation_status = "active"

        precipitation_forecast = "none"
        precipitation_chance = 0
        if forecast and "hourly" in forecast and forecast["hourly"]:
            next_hours = forecast["hourly"][:6]
            max_pop = max([h.get("pop", 0) for h in next_hours], default=0)
            precipitation_chance = int(max_pop * 100)

            if precipitation_chance > 70:
                precipitation_forecast = "very_likely"
            elif precipitation_chance > 40:
                precipitation_forecast = "likely"
            elif precipitation_chance > 20:
                precipitation_forecast = "possible"

        conditions = []

        if temp is not None:
            if weather_config.units == "metric":
                if temp < 0:
                    conditions.append("freezing")
                elif temp < 10:
                    conditions.append("very cold")
                elif temp < 15:
                    conditions.append("chilly")
                elif temp < 25:
                    conditions.append("mild")
                elif temp < 30:
                    conditions.append("warm")
                else:
                    conditions.append("hot")
            else:
                if temp < 32:
                    conditions.append("freezing")
                elif temp < 45:
                    conditions.append("very cold")
                elif temp < 60:
                    conditions.append("chilly")
                elif temp < 75:
                    conditions.append("mild")
                elif temp < 85:
                    conditions.append("warm")
                else:
                    conditions.append("hot")

        if wind_speed is not None:
            if weather_config.units == "metric":
                if wind_speed < 5:
                    wind_description = "calm"
                elif wind_speed < 15:
                    wind_description = "a light breeze"
                elif wind_speed < 25:
                    wind_description = "a moderate breeze"
                elif wind_speed < 40:
                    wind_description = "strong winds"
                else:
                    wind_description = "very strong winds"
            else:
                if wind_speed < 10:
                    wind_description = "calm"
                elif wind_speed < 20:
                    wind_description = "a light breeze"
                elif wind_speed < 30:
                    wind_description = "a moderate breeze"
                elif wind_speed < 45:
                    wind_description = "strong winds"
                else:
                    wind_description = "very strong winds"
        else:
            wind_description = "unknown wind"

        precip_description = ""
        if precipitation_status == "active":
            if rain > snow:
                precip_description = "raining"
            else:
                precip_description = "snowing"
        elif precipitation_forecast != "none":
            if precipitation_forecast == "very_likely":
                precip_description = f"{precipitation_chance}% chance of precipitation"
            elif precipitation_forecast == "likely":
                precip_description = (
                    f"likely to rain soon ({precipitation_chance}% chance)"
                )
            elif precipitation_forecast == "possible":
                precip_description = (
                    f"slight chance of rain ({precipitation_chance}% chance)"
                )

        temp_unit = "°F" if weather_config.units == "imperial" else "°C"
        speed_unit = "mph" if weather_config.units == "imperial" else "km/h"

        feels_diff = ""
        if feels_like is not None and temp is not None:
            diff = feels_like - temp
            if abs(diff) > 2:
                if diff < 0:
                    feels_diff = f"feels colder at {feels_like:.1f}{temp_unit}"
                else:
                    feels_diff = f"feels warmer at {feels_like:.1f}{temp_unit}"

        temperature = f"{temp:.1f}{temp_unit}" if temp is not None else "unknown"

        return {
            "success": True,
            "location": location_name,
            "city": location_data.get("city", ""),
            "country": location_data.get("country", ""),
            "weather_condition": weather_condition,
            "temperature": temperature,
            "feels_like": feels_like,
            "feels_diff": feels_diff,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "wind_description": wind_description,
            "precipitation_status": precipitation_status,
            "precipitation_forecast": precipitation_forecast,
            "precipitation_chance": precipitation_chance,
            "precipitation_description": precip_description,
            "units": weather_config.units,
            "condition_summary": ", ".join(conditions),
            "has_precipitation": precipitation_status != "none"
            or precipitation_forecast != "none",
        }
    except Exception as e:
        print(f"Error getting weather data: {e}")
        return {"success": False, "error": str(e), "location": location_name}


async def get_weather(entities: Dict[str, Any], **context) -> Dict[str, Any]:
    """
    Handle weather inquiries and return weather data

    intent: get_weather
    """
    config = context.get("config")

    location = None
    date = "today"

    if "location" in entities and entities["location"]:
        location = entities["location"][0]["value"]["name"]

    if "date" in entities and entities["date"]:
        date_entity = entities["date"][0]["value"]
        if date_entity.get("type") == "relative":
            date = date_entity.get("relative", "today")
        else:
            date = date_entity.get("date", "today")

    weather_data = await get_weather_data(location, config)

    if not weather_data.get("success", False):
        return {
            "data": {
                "error": weather_data.get("error", "Unknown error"),
                "location": weather_data.get("location", location or "your location"),
                "date": date,
                "weather_condition": "unknown",
                "temperature": "unknown",
            }
        }
    return {
        "data": {
            "location": weather_data.get("location"),
            "date": date,
            "weather_condition": weather_data.get("weather_condition", "unknown"),
            "temperature": weather_data.get("temperature"),
            "feels_like": weather_data.get("feels_diff") or "",
            "humidity": f"{weather_data.get('humidity')}%",
            "wind": weather_data.get("wind_description", ""),
            "precipitation": weather_data.get("precipitation_description", ""),
            "condition_summary": weather_data.get("condition_summary", ""),
            "has_precipitation": weather_data.get("has_precipitation", False),
        }
    }


async def get_temperature(entities: Dict[str, Any], **context) -> Dict[str, Any]:
    """
    Handle temperature inquiries and return detailed temperature data

    intent: get_temperature
    """

    config = context.get("config")

    location = None
    date = "today"

    if "location" in entities and entities["location"]:
        location = entities["location"][0]["value"]["name"]

    if "date" in entities and entities["date"]:
        date_entity = entities["date"][0]["value"]
        if date_entity.get("type") == "relative":
            date = date_entity.get("relative", "today")
        else:
            date = date_entity.get("date", "today")

    weather_data = await get_weather_data(location, config)

    if not weather_data.get("success", False):
        return {
            "data": {
                "error": weather_data.get("error", "Unknown error"),
                "location": weather_data.get("location", location or "your location"),
                "date": date,
                "temperature": "unknown",
            }
        }

    temperature = weather_data.get("temperature")
    feels_like = weather_data.get("feels_like")
    feels_diff = weather_data.get("feels_diff", "")
    units = weather_data.get("units", "metric")
    condition_summary = weather_data.get("condition_summary", "")

    high_temp = None
    low_temp = None
    temp_unit = "°F" if units == "imperial" else "°C"

    forecast = weather_data.get("forecast")
    if forecast and "daily" in forecast and forecast["daily"]:
        today_forecast = forecast["daily"][0]
        if "temp" in today_forecast:
            if "max" in today_forecast["temp"]:
                high_temp = f"{today_forecast['temp']['max']:.1f}{temp_unit}"
            if "min" in today_forecast["temp"]:
                low_temp = f"{today_forecast['temp']['min']:.1f}{temp_unit}"

    temp_description = condition_summary
    if not temp_description:
        if units == "metric":
            if feels_like is not None:
                if feels_like < 0:
                    temp_description = "below freezing"
                elif feels_like < 10:
                    temp_description = "very cold"
                elif feels_like < 15:
                    temp_description = "cold"
                elif feels_like < 20:
                    temp_description = "mild"
                elif feels_like < 25:
                    temp_description = "warm"
                elif feels_like < 30:
                    temp_description = "very warm"
                else:
                    temp_description = "hot"
        else:  # imperial
            if feels_like is not None:
                if feels_like < 32:
                    temp_description = "below freezing"
                elif feels_like < 45:
                    temp_description = "very cold"
                elif feels_like < 55:
                    temp_description = "cold"
                elif feels_like < 65:
                    temp_description = "mild"
                elif feels_like < 75:
                    temp_description = "warm"
                elif feels_like < 85:
                    temp_description = "very warm"
                else:
                    temp_description = "hot"

    return {
        "data": {
            "location": weather_data.get("location"),
            "date": date,
            "temperature": temperature,
            "feels_like": feels_diff,
            "temperature_description": temp_description,
            "high_temperature": high_temp,
            "low_temperature": low_temp,
            "has_high_low": high_temp is not None and low_temp is not None,
            "humidity": f"{weather_data.get('humidity')}%"
            if weather_data.get("humidity") is not None
            else "unknown",
        }
    }


async def get_precipitation(entities: Dict[str, Any], **context) -> Dict[str, Any]:
    """
    Handle precipitation inquiries and return precipitation data

    intent: get_precipitation
    """
    config = context.get("config")
    text = context.get("text", "")

    location = None
    date = "today"

    if "location" in entities and entities["location"]:
        location = entities["location"][0]["value"]["name"]

    if "date" in entities and entities["date"]:
        date_entity = entities["date"][0]["value"]
        if date_entity.get("type") == "relative":
            date = date_entity.get("relative", "today")
        else:
            date = date_entity.get("date", "today")

    weather_data = await get_weather_data(location, config)

    if not weather_data.get("success", False):
        return {
            "data": {
                "error": weather_data.get("error", "Unknown error"),
                "location": weather_data.get("location", location or "your location"),
                "date": date,
                "precipitation": "unknown",
            }
        }

    is_umbrella_query = "umbrella" in text.lower() or "rain" in text.lower()

    precipitation_description = weather_data.get("precipitation_description", "")
    if not precipitation_description and not weather_data.get(
        "has_precipitation", False
    ):
        precipitation_description = "no precipitation expected"

    chance = weather_data.get("precipitation_chance", 0)
    rain = weather_data.get("rain", 0)
    snow = weather_data.get("snow", 0)

    detailed_info = ""
    if rain > 0:
        detailed_info = f"{rain}mm of rain"
    elif snow > 0:
        detailed_info = f"{snow}mm of snow"
    elif chance > 0:
        detailed_info = f"{chance}% chance of precipitation"
    else:
        detailed_info = "dry conditions"

    return {
        "data": {
            "location": weather_data.get("location"),
            "date": date,
            "precipitation": precipitation_description or detailed_info,
            "precipitation_chance": chance,
            "has_precipitation": weather_data.get("has_precipitation", False),
            "umbrella_needed": weather_data.get("umbrella_needed", False),
            "query_type": "umbrella" if is_umbrella_query else "general",
            "text": text,
        }
    }


async def get_wind(entities: Dict[str, Any], **context) -> Dict[str, Any]:
    """
    Handle wind inquiries and return wind data

    intent: get_wind
    """
    config = context.get("config")

    location = None
    date = "today"

    if "location" in entities and entities["location"]:
        location = entities["location"][0]["value"]["name"]

    if "date" in entities and entities["date"]:
        date_entity = entities["date"][0]["value"]
        if date_entity.get("type") == "relative":
            date = date_entity.get("relative", "today")
        else:
            date = date_entity.get("date", "today")

    weather_data = await get_weather_data(location, config)

    if not weather_data.get("success", False):
        return {
            "data": {
                "error": weather_data.get("error", "Unknown error"),
                "location": weather_data.get("location", location or "your location"),
                "date": date,
                "wind": "unknown",
            }
        }

    wind_speed = weather_data.get("wind_speed")
    wind_direction = weather_data.get("wind_direction_text", "")
    wind_description = weather_data.get("wind_description", "")
    speed_unit = weather_data.get("speed_unit", "km/h")

    detailed_wind = ""
    if wind_speed is not None and wind_direction:
        detailed_wind = (
            f"{wind_description} from the {wind_direction} at {wind_speed} {speed_unit}"
        )
    elif wind_speed is not None:
        detailed_wind = f"{wind_description} at {wind_speed} {speed_unit}"
    else:
        detailed_wind = wind_description

    is_windy = False
    if wind_speed is not None:
        if weather_data.get("units") == "metric":
            is_windy = wind_speed > 20  # km/h
        else:
            is_windy = wind_speed > 12  # mph

    return {
        "data": {
            "location": weather_data.get("location"),
            "date": date,
            "wind": detailed_wind,
            "wind_speed": f"{wind_speed} {speed_unit}"
            if wind_speed is not None
            else "unknown",
            "wind_direction": wind_direction,
            "is_windy": is_windy,
        }
    }

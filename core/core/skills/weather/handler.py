from typing import Any, Dict

import requests


def get_current_location_from_ip(device_id=None) -> Dict[str, Any]:
    try:
        response = requests.get("http://ip-api.com/json/")
        if response.status_code == 200:
            data = response.json()
            return {
                "city": data.get("city"),
                "country": data.get("country"),
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "success": True,
            }
    except Exception as e:
        print(f"Error getting location from IP: {e}")

    return {"success": False}


def get_weather(entities: Dict[str, Any], **context) -> Dict[str, Any]:
    """
    Handle weather inquiries and return weather data

    intent: get_weather
    """
    config = context.get("config")
    weather_config = config.weather
    device_id = context.get("device_id", "unknown")

    api_key = weather_config.api_key
    if not api_key:
        return {
            "data": {
                "error": "API key not configured",
                "weather_condition": "unknown",
                "temperature": "unknown",
            }
        }

    units = weather_config.units

    # Process location from entities
    location = None
    date = "today"

    # Extract location from entities if available
    if "location" in entities and entities["location"]:
        location = entities["location"][0]["value"]["name"]

    # Extract date from entities if available
    if "date" in entities and entities["date"]:
        date_entity = entities["date"][0]["value"]
        if date_entity.get("type") == "relative":
            date = date_entity.get("relative", "today")
        else:
            date = date_entity.get("date", "today")

    # Use current location if not specified
    if not location:
        location_data = get_current_location_from_ip(device_id)
        if location_data.get("success"):
            location = location_data.get("city", "unknown location")

    try:
        # This would be a real API call in production
        # For demo, return mock data
        weather_data = {
            "location": location or "your location",
            "date": date,
            "weather_condition": "sunny",
            "temperature": "72°F" if units == "imperial" else "22°C",
            "precipitation": "10% chance of rain",
            "wind": "light breeze",
        }

        return {"data": weather_data}

    except Exception as e:
        return {
            "data": {
                "error": str(e),
                "location": location or "unknown",
                "date": date,
                "weather_condition": "unknown",
                "temperature": "unknown",
            }
        }

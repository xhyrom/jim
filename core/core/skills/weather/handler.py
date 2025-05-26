import requests
from typing import Dict, Any


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
    except:
        pass

    return {"success": False}


def get_weather(entities: Dict[str, Any], **context) -> Dict[str, Any]:
    config = context.get("config")
    weather_config = config.skills.weather

    api_key = weather_config.api_key
    if not api_key:
        return {
            "response": "I'm sorry, but the weather service is not properly configured. Please add an OpenWeather API key to the configuration.",
            "action": None,
            "data": {"error": "API key not configured"},
        }

    units = weather_config.units

    location = entities.get("location", "")
    device_id = context.get("device_id", "unknown")

    use_current_location = False
    if not location or location.lower() in [
        "here",
        "current location",
        "this place",
        "your current location",
    ]:
        use_current_location = True
        location_data = get_current_location_from_ip(device_id)

        if location_data.get("success"):
            location = location_data.get("city", "")
            lat = location_data.get("lat")
            lon = location_data.get("lon")
        else:
            return {
                "response": "I'm sorry, I couldn't determine your current location. Could you please specify a location?",
                "action": None,
                "data": {"error": "Could not determine current location"},
            }

    try:
        openweather_base_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"appid": api_key, "units": units}

        if use_current_location and "lat" in locals() and "lon" in locals():
            params["lat"] = lat
            params["lon"] = lon
        else:
            params["q"] = location

        response = requests.get(openweather_base_url, params=params)
        response.raise_for_status()

        weather_data = response.json()

        city_name = weather_data["name"]
        country_code = weather_data["sys"]["country"]
        condition = weather_data["weather"][0]["description"]
        temperature = round(weather_data["main"]["temp"], 1)
        feels_like = round(weather_data["main"]["feels_like"], 1)
        humidity = weather_data["main"]["humidity"]
        wind_speed = weather_data["wind"]["speed"]

        temp_unit = "celsius" if units == "metric" else "fahrenheit"
        wind_unit = "meters per second" if units == "metric" else "miles per hour"

        response_text = (
            f"The weather in {city_name}, {country_code} is {condition} with a temperature of {temperature} {temp_unit}, "
            f"feels like {feels_like} {temp_unit}. The humidity is {humidity}% and wind speed is {wind_speed} {wind_unit}."
        )

        return {
            "response": response_text,
            "action": None,
            "data": {
                "location": f"{city_name}, {country_code}",
                "condition": condition,
                "temperature": f"{temperature}{temp_unit}",
                "feels_like": f"{feels_like}{temp_unit}",
                "humidity": f"{humidity}%",
                "wind_speed": f"{wind_speed} {wind_unit}",
                "raw": weather_data,
            },
        }

    except Exception as e:
        return {
            "response": f"I'm sorry, I encountered an issue while checking the weather for {location}.",
            "action": None,
            "data": {"error": str(e), "location": location},
        }

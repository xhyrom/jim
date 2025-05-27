from typing import Any, Dict, Optional, Tuple

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


def parse_weather_condition(weather_data: Dict[str, Any], units: str) -> Dict[str, Any]:
    city_name = weather_data["name"]
    country_code = weather_data["sys"]["country"]
    condition = weather_data["weather"][0]["description"]
    condition_main = weather_data["weather"][0]["main"]
    condition_id = weather_data["weather"][0]["id"]
    temperature = round(weather_data["main"]["temp"], 1)
    feels_like = round(weather_data["main"]["feels_like"], 1)
    humidity = weather_data["main"]["humidity"]
    wind_speed = weather_data["wind"]["speed"]
    pressure = weather_data["main"]["pressure"]
    visibility = weather_data.get("visibility", 0) / 1000  # Convert to km

    clouds = weather_data.get("clouds", {}).get("all", 0)
    rain_1h = weather_data.get("rain", {}).get("1h", 0)
    snow_1h = weather_data.get("snow", {}).get("1h", 0)
    sunrise = weather_data["sys"]["sunrise"]
    sunset = weather_data["sys"]["sunset"]

    temp_unit = "°C" if units == "metric" else "°F"
    wind_unit = "m/s" if units == "metric" else "mph"

    return {
        "location": f"{city_name}, {country_code}",
        "condition": {
            "description": condition,
            "main": condition_main,
            "id": condition_id,
        },
        "temperature": {
            "current": temperature,
            "feels_like": feels_like,
            "unit": temp_unit,
        },
        "humidity": humidity,
        "wind": {"speed": wind_speed, "unit": wind_unit},
        "pressure": pressure,
        "visibility": visibility,
        "clouds": clouds,
        "precipitation": {"rain": rain_1h, "snow": snow_1h},
        "sun": {"sunrise": sunrise, "sunset": sunset},
    }


def create_weather_response(weather_data: Dict[str, Any], units: str) -> str:
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
        f"The weather in {city_name}, {country_code} is {condition} with a temperature of {temperature}° {temp_unit}, "
        f"feels like {feels_like}° {temp_unit}. The humidity is {humidity}% and wind speed is {wind_speed} {wind_unit}."
    )

    return response_text


def get_location_and_condition(
    entities: Dict[str, Any], device_id: str
) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
    """Extract location and condition from entities, or get current location if not provided."""
    location = entities.get("location", "")
    condition = entities.get("condition")

    use_current_location = False
    lat, lon = None, None

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
            location_info = {"lat": lat, "lon": lon}
        else:
            return (
                None,
                None,
                "I couldn't determine your current location. Could you please specify a location?",
            )
    else:
        location_info = None

    return location, location_info, None


def get_weather(entities: Dict[str, Any], **context) -> Dict[str, Any]:
    config = context.get("config")
    weather_config = config.skills.weather
    device_id = context.get("device_id", "unknown")

    api_key = weather_config.api_key
    if not api_key:
        return {
            "response": "I'm sorry, but the weather service is not properly configured. Please add an OpenWeather API key to the configuration.",
            "action": None,
            "data": {"error": "API key not configured"},
        }

    units = weather_config.units

    location, location_info, error_message = get_location_and_condition(
        entities, device_id
    )

    if error_message:
        return {
            "response": error_message,
            "action": None,
            "data": {"error": error_message},
        }

    condition = entities.get("condition")

    try:
        openweather_base_url = "https://api.openweathermap.org/data/3.0/onecall"
        params = {"appid": api_key, "units": units}

        if location_info and "lat" in location_info and "lon" in location_info:
            params["lat"] = location_info["lat"]
            params["lon"] = location_info["lon"]
        else:
            params["q"] = location

        response = requests.get(openweather_base_url, params=params)
        response.raise_for_status()
        weather_data = response.json()

        parsed_data = parse_weather_condition(weather_data, units)

        if condition:
            condition = condition.lower()
            current_condition = parsed_data["condition"]["main"].lower()

            if condition == current_condition:
                response_text = f"Yes, it is {condition} in {parsed_data['location']}."
            else:
                response_text = f"No, it is not {condition} in {parsed_data['location']}. The current condition is {current_condition}."
        else:
            response_text = create_weather_response(weather_data, units)

        return {
            "response": response_text,
            "action": None,
            "data": parsed_data,
        }

    except Exception as e:
        return {
            "response": f"I'm sorry, I encountered an issue while checking the weather for {location}.",
            "action": None,
            "data": {"error": str(e), "location": location},
        }

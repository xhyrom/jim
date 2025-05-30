import aiohttp
from typing import Dict, Any, Optional

from . import WeatherService, WeatherServiceRegistry


@WeatherServiceRegistry.register("openweathermap")
class OpenWeatherMapService(WeatherService):
    """OpenWeatherMap API service implementation"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openweathermap.org/data/2.5/",
    ):
        self.api_key = api_key
        self.base_url = base_url

    async def get_current_weather(
        self, lat: float, lon: float, units: str = "metric"
    ) -> Dict[str, Any]:
        """Get current weather for a location using OpenWeatherMap API"""
        params = {
            "lat": lat,
            "lon": lon,
            "units": units,
            "appid": self.api_key,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}weather", params=params
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(
                        f"OpenWeatherMap API error: {response.status} - {error_text}"
                    )

                data = await response.json()

                return {
                    "temperature": data.get("main", {}).get("temp"),
                    "feels_like": data.get("main", {}).get("feels_like"),
                    "pressure": data.get("main", {}).get("pressure"),
                    "humidity": data.get("main", {}).get("humidity"),
                    "weather_condition": data.get("weather", [{}])[0].get(
                        "main", "Unknown"
                    ),
                    "weather_description": data.get("weather", [{}])[0].get(
                        "description", "Unknown"
                    ),
                    "weather_icon": data.get("weather", [{}])[0].get("icon"),
                    "wind_speed": data.get("wind", {}).get("speed"),
                    "wind_direction": data.get("wind", {}).get("deg"),
                    "clouds": data.get("clouds", {}).get("all"),
                    "rain": data.get("rain", {}).get("1h", 0),
                    "snow": data.get("snow", {}).get("1h", 0),
                    "timestamp": data.get("dt"),
                    "units": units,
                }

    async def get_forecast(
        self, lat: float, lon: float, units: str = "metric"
    ) -> Dict[str, Any]:
        """Get weather forecast for a location using OpenWeatherMap API"""
        params = {
            "lat": lat,
            "lon": lon,
            "units": units,
            "appid": self.api_key,
            "cnt": 40,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}forecast", params=params
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(
                        f"OpenWeatherMap API error: {response.status} - {error_text}"
                    )

                data = await response.json()

                hourly = []
                daily = {}

                for item in data.get("list", []):
                    timestamp = item.get("dt")
                    date = item.get("dt_txt", "").split(" ")[0]

                    hourly_item = {
                        "dt": timestamp,
                        "temp": item.get("main", {}).get("temp"),
                        "feels_like": item.get("main", {}).get("feels_like"),
                        "weather": item.get("weather", [{}]),
                        "pop": item.get("pop", 0),
                    }

                    hourly.append(hourly_item)

                    if date not in daily:
                        daily[date] = {
                            "dt": timestamp,
                            "temp": {
                                "min": item.get("main", {}).get("temp_min", 999),
                                "max": item.get("main", {}).get("temp_max", -999),
                            },
                            "weather": item.get("weather", [{}]),
                            "pop": item.get("pop", 0),
                        }
                    else:
                        temp = item.get("main", {}).get("temp_min")
                        if temp < daily[date]["temp"]["min"]:
                            daily[date]["temp"]["min"] = temp

                        temp = item.get("main", {}).get("temp_max")
                        if temp > daily[date]["temp"]["max"]:
                            daily[date]["temp"]["max"] = temp

                        if item.get("pop", 0) > daily[date]["pop"]:
                            daily[date]["pop"] = item.get("pop", 0)

                return {
                    "hourly": hourly,
                    "daily": list(daily.values()),
                    "units": units,
                }

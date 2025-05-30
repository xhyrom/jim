from typing import Dict, Any
import random
from datetime import datetime, timedelta

from . import WeatherService, WeatherServiceRegistry


@WeatherServiceRegistry.register("mock")
class MockWeatherService(WeatherService):
    """Mock weather service for testing or when no API key is available"""

    def __init__(self, **kwargs):
        pass

    async def get_current_weather(
        self, lat: float, lon: float, units: str = "metric"
    ) -> Dict[str, Any]:
        """Generate mock current weather data"""
        temp = random.uniform(10, 30) if units == "metric" else random.uniform(50, 86)
        feels_like = temp - random.uniform(-2, 2)

        weather_conditions = [
            "Clear",
            "Clouds",
            "Rain",
            "Drizzle",
            "Thunderstorm",
            "Snow",
            "Mist",
        ]
        descriptions = {
            "Clear": "clear sky",
            "Clouds": [
                "few clouds",
                "scattered clouds",
                "broken clouds",
                "overcast clouds",
            ],
            "Rain": ["light rain", "moderate rain", "heavy rain"],
            "Drizzle": "light intensity drizzle",
            "Thunderstorm": "thunderstorm",
            "Snow": ["light snow", "snow", "heavy snow"],
            "Mist": "mist",
        }

        condition = random.choice(weather_conditions)

        if isinstance(descriptions[condition], list):
            description = random.choice(descriptions[condition])
        else:
            description = descriptions[condition]

        return {
            "temperature": round(temp, 1),
            "feels_like": round(feels_like, 1),
            "pressure": random.randint(990, 1030),
            "humidity": random.randint(30, 95),
            "weather_condition": condition,
            "weather_description": description,
            "weather_icon": "01d" if condition == "Clear" else "02d",
            "wind_speed": round(random.uniform(0, 15), 1),
            "wind_direction": random.randint(0, 359),
            "clouds": random.randint(0, 100),
            "rain": round(random.uniform(0, 5), 1) if condition == "Rain" else 0,
            "snow": round(random.uniform(0, 5), 1) if condition == "Snow" else 0,
            "timestamp": int(datetime.now().timestamp()),
            "units": units,
        }

    async def get_forecast(
        self, lat: float, lon: float, units: str = "metric"
    ) -> Dict[str, Any]:
        """Generate mock forecast data"""
        hourly = []
        daily = []

        # Generate hourly forecast data for the next 24 hours
        for i in range(24):
            current_time = datetime.now() + timedelta(hours=i)

            # Create some temperature variation throughout the day
            base_temp = (
                random.uniform(15, 25) if units == "metric" else random.uniform(59, 77)
            )
            hour_temp = base_temp + 5 * (-0.5 + ((current_time.hour % 24) / 12))

            hourly.append(
                {
                    "dt": int((current_time).timestamp()),
                    "temp": round(hour_temp, 1),
                    "feels_like": round(hour_temp - random.uniform(-2, 2), 1),
                    "weather": [
                        {
                            "main": "Clear" if random.random() > 0.3 else "Clouds",
                            "description": "clear sky"
                            if random.random() > 0.3
                            else "few clouds",
                            "icon": "01d"
                            if current_time.hour > 6 and current_time.hour < 20
                            else "01n",
                        }
                    ],
                }
            )

        # Generate daily forecast for the next 7 days
        for i in range(7):
            current_date = datetime.now() + timedelta(days=i)

            if units == "metric":
                min_temp = random.uniform(10, 18)
                max_temp = random.uniform(20, 30)
            else:  # imperial
                min_temp = random.uniform(50, 65)
                max_temp = random.uniform(68, 86)

            daily.append(
                {
                    "dt": int((current_date).timestamp()),
                    "temp": {"min": round(min_temp, 1), "max": round(max_temp, 1)},
                    "weather": [
                        {
                            "main": "Clear" if random.random() > 0.3 else "Clouds",
                            "description": "clear sky"
                            if random.random() > 0.3
                            else "few clouds",
                            "icon": "01d",
                        }
                    ],
                    "pop": random.random(),  # Probability of precipitation
                }
            )

        return {"hourly": hourly, "daily": daily, "units": units}

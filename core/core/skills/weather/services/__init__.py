from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type


class WeatherService(ABC):
    """Abstract base class for weather services"""

    @abstractmethod
    async def get_current_weather(
        self, lat: float, lon: float, units: str = "metric"
    ) -> Dict[str, Any]:
        """Get current weather for a location"""
        pass

    @abstractmethod
    async def get_forecast(
        self, lat: float, lon: float, units: str = "metric"
    ) -> Dict[str, Any]:
        """Get weather forecast for a location"""
        pass


class WeatherServiceRegistry:
    _services: Dict[str, Type[WeatherService]] = {}

    @classmethod
    def register(cls, name: str):
        """Register a weather service implementation"""

        def decorator(service_class):
            cls._services[name] = service_class
            return service_class

        return decorator

    @classmethod
    def get_service(cls, name: str, **kwargs) -> Optional[WeatherService]:
        """Get a weather service by name"""
        service_class = cls._services.get(name)
        if service_class:
            return service_class(**kwargs)
        return None


from .openweathermap import OpenWeatherMapService
from .mock import MockWeatherService

__all__ = [
    "WeatherService",
    "WeatherServiceRegistry",
    "OpenWeatherMapService",
    "MockWeatherService",
]

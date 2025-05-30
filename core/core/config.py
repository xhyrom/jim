from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tomli


@dataclass
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 31415

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ServerConfig":
        return ServerConfig(
            host=data.get("host", "127.0.0.1"), port=data.get("port", 31415)
        )


@dataclass
class WeatherConfig:
    base_url: str = "https://api.openweathermap.org/data/2.5/"
    api_key: str = ""
    implementation: str = "openweathermap"
    units: str = "metric"

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "WeatherConfig":
        return WeatherConfig(
            base_url=data.get("base_url", "https://api.openweathermap.org/data/2.5/"),
            api_key=data.get("api_key", ""),
            implementation=data.get("implementation", "openweathermap"),
            units=data.get("units", "metric"),
        )


@dataclass
class GeocodingConfig:
    base_url: str = "https://nominatim.openstreetmap.org/"
    user_agent: str = "jim"
    implementation: str = "nominatim"

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "GeocodingConfig":
        return GeocodingConfig(
            base_url=data.get("base_url", "https://nominatim.openstreetmap.org/"),
            user_agent=data.get("user_agent", "jim"),
            implementation=data.get("implementation", "nominatim"),
        )


@dataclass
class AppConfig:
    server: ServerConfig = field(default_factory=ServerConfig)
    weather: WeatherConfig = field(default_factory=WeatherConfig)
    geocoding: GeocodingConfig = field(default_factory=GeocodingConfig)
    debug: bool = False

    @staticmethod
    def from_file(path: Path) -> "AppConfig":
        try:
            with open(path, "rb") as f:
                data = tomli.load(f)

            return AppConfig.from_dict(data)
        except Exception as e:
            print(f"Error loading config: {e}")
            return AppConfig()

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "AppConfig":
        return AppConfig(
            server=ServerConfig.from_dict(data.get("server", {})),
            weather=WeatherConfig.from_dict(data.get("weather", {})),
            geocoding=GeocodingConfig.from_dict(data.get("geocoding", {})),
            debug=data.get("debug", False),
        )

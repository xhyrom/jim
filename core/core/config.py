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
class LLMConfig:
    enabled: bool = True
    provider: str = "mock"
    fallback_threshold: float = 0.6
    system_prompt: str = ""
    contexts: list[str] = field(default_factory=list)
    streaming: bool = False
    models: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "openai": {"api_key": "", "model": "gpt-3.5-turbo", "base_url": ""},
            "anthropic": {"api_key": "", "model": "claude-instant-1"},
            "gemini": {"api_key": "", "model": "gemini-pro"},
            "ollama": {"base_url": "http://localhost:11434", "model": "llama3"},
            "huggingface": {"api_key": "", "model": "meta-llama/Llama-2-7b-chat-hf", "base_url": ""},
            "bitnet": {"api_key": "", "model": "microsoft/BitNet-b1.58-1.4B", "local": True, "device": "cuda", "use_hf": True},
            "mock": {"max_tokens": 50},
        }
    )

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "LLMConfig":
        models = data.get("models", {})
        return LLMConfig(
            enabled=data.get("enabled", True),
            provider=data.get("provider", "mock"),
            fallback_threshold=data.get("fallback_threshold", 0.6),
            system_prompt=data.get("system_prompt", ""),
            contexts=data.get("contexts", []),
            streaming=data.get("streaming", False),
            models=models,
        )


@dataclass
class AppConfig:
    server: ServerConfig = field(default_factory=ServerConfig)
    weather: WeatherConfig = field(default_factory=WeatherConfig)
    geocoding: GeocodingConfig = field(default_factory=GeocodingConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
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
            llm=LLMConfig.from_dict(data.get("llm", {})),
            debug=data.get("debug", False),
        )

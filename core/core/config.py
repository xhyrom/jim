from dataclasses import dataclass, field
from json import loads
from pathlib import Path
from typing import Any, Optional

_DIR = Path(__file__).parent
_PROJECT_ROOT = _DIR.parent.parent
_CONFIG_PATH = _PROJECT_ROOT / "config.json"

@dataclass
class WeatherSkillConfig:
    api_key: str = ""
    units: str = "metric"

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "WeatherSkillConfig":
        return WeatherSkillConfig(
            api_key=data.get("api_key", ""),
            units=data.get("units", "metric")
        )


@dataclass
class SkillConfig:
    weather: WeatherSkillConfig = field(default_factory=WeatherSkillConfig)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "SkillConfig":
        return SkillConfig(
            weather=WeatherSkillConfig.from_dict(data.get("weather", {})),
        )

@dataclass
class Config:
    host: str = "0.0.0.0"
    port: int = 31415
    debug: bool = False
    skills: SkillConfig = field(default_factory=SkillConfig)

    @staticmethod
    def from_file(path: Path) -> "Config":
        try:
            with open(path) as f:
                data = loads(f.read())

            return Config.from_dict(data)
        except:
            return Config()

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Config":
        return Config(
            host=data.get("host", "0.0.0.0"),
            port=data.get("port", 31415),
            debug=data.get("debug", False),
            skills=SkillConfig.from_dict(data["skills"]) if "skills" in data else SkillConfig()
        )

_config: Optional[Config] = None

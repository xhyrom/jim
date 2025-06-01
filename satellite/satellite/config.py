from dataclasses import dataclass, field
from enum import Enum, auto
from json import loads
from pathlib import Path
from typing import Any, Optional

from .asr.asr import AutomaticSpeechRecognitionService
from .asr.google import GoogleService
from .asr.vosk import VoskService
from .asr.whisper import WhisperService
from .tts.piper import PiperService
from .tts.tts import TextToSpeechService

_DIR = Path(__file__).parent
_MODELS_DIR = _DIR / ".." / ".." / "models"


class ASRType(Enum):
    WHISPER = auto()
    GOOGLE = auto()
    VOSK = auto()


class TTSType(Enum):
    PIPER = auto()


@dataclass
class ASRConfig:
    type: ASRType = ASRType.WHISPER
    model_path: Optional[str] = "base"
    api_key: Optional[str] = None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ASRConfig":
        return ASRConfig(
            type=ASRType[data["type"].upper()],
            model_path=data.get("model_path"),
            api_key=data.get("api_key"),
        )

    def create_service(self) -> AutomaticSpeechRecognitionService:
        match self.type:
            case ASRType.WHISPER:
                if not self.model_path:
                    raise ValueError("model_path is required for Whisper ASR")
                return WhisperService(self.model_path)
            case ASRType.GOOGLE:
                return GoogleService(self.api_key)
            case ASRType.VOSK:
                if not self.model_path:
                    raise ValueError("model_path is required for Vosk ASR")
                return VoskService(Path(self.model_path))
            case _:
                raise ValueError(f"Unknown ASR type: {self.type}")


@dataclass
class TTSConfig:
    type: TTSType = TTSType.PIPER
    model_path: str = str(_MODELS_DIR / "piper" / "en_GB-cori-high.onnx")

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "TTSConfig":
        return TTSConfig(
            type=TTSType[data["type"].upper()],
            model_path=data["model_path"],
        )

    def create_service(self) -> TextToSpeechService:
        match self.type:
            case TTSType.PIPER:
                return PiperService(Path(self.model_path))
            case _:
                raise ValueError(f"Unknown TTS type: {self.type}")


@dataclass
class WakeConfig:
    model_paths: list[str] = field(
        default_factory=lambda: [
            str(_MODELS_DIR / "openwakeword" / "hey_jarvis.tflite")
        ]
    )
    threshold: float = 0.5

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "WakeConfig":
        return WakeConfig(
            model_paths=data["model_paths"],
            threshold=data.get("threshold", 0.5),
        )


@dataclass
class CoreConfig:
    url: str = "http://localhost:31415"
    api_key: Optional[str] = None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "CoreConfig":
        return CoreConfig(
            url=data.get("url", "http://localhost:31415"), api_key=data.get("api_key")
        )


class LEDDriverType(Enum):
    AUTO = auto()
    APA102 = auto()
    NEOPIXEL = auto()
    MOCK = auto()


@dataclass
class LEDSchedule:
    enabled: bool = True
    start_hour: int = 7  # 7 AM
    end_hour: int = 22  # 10 PM


@dataclass
class LEDConfig:
    driver_type: LEDDriverType = LEDDriverType.AUTO
    num_leds: int = 3
    brightness: int = 10
    base_color: tuple[int, int, int] = (255, 80, 0)
    schedule: LEDSchedule = field(default_factory=LEDSchedule)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "LEDConfig":
        schedule_data = data.get("schedule", {})
        schedule = LEDSchedule(
            enabled=schedule_data.get("enabled", True),
            start_hour=schedule_data.get("start_hour", 7),
            end_hour=schedule_data.get("end_hour", 22),
        )

        color = data.get("base_color", (255, 80, 0))
        if isinstance(color, str):
            if color.startswith("#") and len(color) == 7:
                try:
                    r = int(color[1:3], 16)
                    g = int(color[3:5], 16)
                    b = int(color[5:7], 16)
                    color = (r, g, b)
                except ValueError:
                    pass

        return LEDConfig(
            driver_type=LEDDriverType[data.get("driver_type", "AUTO").upper()],
            num_leds=data.get("num_leds", 3),
            brightness=data.get("brightness", 10),
            base_color=color,
            schedule=schedule,
        )


@dataclass
class Config:
    asr: ASRConfig = field(default_factory=ASRConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    wake: WakeConfig = field(default_factory=WakeConfig)
    core: CoreConfig = field(default_factory=CoreConfig)
    led: LEDConfig = field(default_factory=LEDConfig)

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
            asr=ASRConfig.from_dict(data["asr"]) if "asr" in data else ASRConfig(),
            tts=TTSConfig.from_dict(data["tts"]) if "tts" in data else TTSConfig(),
            wake=WakeConfig.from_dict(data["wake"]) if "wake" in data else WakeConfig(),
            led=LEDConfig.from_dict(data["led"]) if "led" in data else LEDConfig(),
        )

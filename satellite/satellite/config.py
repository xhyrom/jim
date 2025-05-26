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


@dataclass
class Config:
    asr: ASRConfig = field(default_factory=ASRConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    wake: WakeConfig = field(default_factory=WakeConfig)
    core: CoreConfig = field(default_factory=CoreConfig)

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
        )

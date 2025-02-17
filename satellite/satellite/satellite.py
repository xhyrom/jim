from enum import Enum, auto
from pathlib import Path

from .asr.asr import AutomaticSpeechRecognitionService
from .asr.whisper import WhisperService
from .microphone import MicrophoneInput
from .wake import WakeService

_DIR = Path(__file__).parent
_MODELS_DIR = _DIR / ".." / ".." / "models"


class State(Enum):
    OFF = auto()
    IDLE = auto()
    LISTENING = auto()
    THINKING = auto()
    SPEAKING = auto()


class Satellite:
    state: State

    microphone: MicrophoneInput

    wake_service: WakeService
    asr_service: AutomaticSpeechRecognitionService

    def __init__(self) -> None:
        self.state = State.OFF

        self.microphone = MicrophoneInput()

        self.wake_service = WakeService(
            [_MODELS_DIR / "openwakeword" / "hey_jarvis.tflite"],
            0.5,
        )
        self.asr_service = WhisperService("base")

    async def run(self) -> None:
        self.state = State.IDLE

        while True:
            if self.wake_service.run(self.microphone):
                self.state = State.LISTENING

                print("Listening...")
                print("res ", self.asr_service.run(self.microphone))

                self.state = State.IDLE

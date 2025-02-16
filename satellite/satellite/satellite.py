from enum import Enum, auto
from pathlib import Path

from .wake import WakeService
from .whisper import WhisperService

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
    wake_service: WakeService

    def __init__(self) -> None:
        self.state = State.OFF

        self.wake_service = WakeService(
            [_MODELS_DIR / "openwakeword" / "hey_jarvis.tflite"],
            0.5,
        )
        self.whisper_service = WhisperService("base")

    async def run(self) -> None:
        self.state = State.IDLE

        while True:
            if self.wake_service.run():
                self.state = State.LISTENING

                print("Listening...")
                self.whisper_service.run()

                self.state = State.IDLE

from enum import Enum, auto
from pathlib import Path

from .wake import WakeService

_DIR = Path(__file__).parent
_MODELS_DIR = _DIR / ".." / ".." / "models" / "satellite"


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
            [_MODELS_DIR / "hey_jarvis.tflite"],
            0.5,
        )

    async def run(self) -> None:
        self.state = State.IDLE

        while True:
            print(self.wake_service.run())

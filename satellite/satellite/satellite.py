from enum import Enum, auto
from pathlib import Path

from .asr.asr import AutomaticSpeechRecognitionService
from .asr.whisper import WhisperService
from .microphone import MicrophoneInput
from .speaker import SpeakerOutput
from .tts.piper import PiperService
from .tts.tts import TextToSpeechService
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
    speaker: SpeakerOutput

    wake_service: WakeService
    asr_service: AutomaticSpeechRecognitionService
    tts_service: TextToSpeechService

    def __init__(self) -> None:
        self.state = State.OFF

        self.microphone = MicrophoneInput()
        self.speaker = SpeakerOutput()

        self.wake_service = WakeService(
            [_MODELS_DIR / "openwakeword" / "hey_jarvis.tflite"],
            0.5,
        )
        self.asr_service = WhisperService("base")
        self.tts_service = PiperService(
            _MODELS_DIR / "piper" / "en_US-ryan-medium.onnx"
        )

    async def run(self) -> None:
        self.state = State.IDLE

        while True:
            if not self.wake_service.run(self.microphone):
                pass

            self.state = State.LISTENING

            print("Listening...")
            res = self.asr_service.run(self.microphone)
            print("Heard:", res)

            self.state = State.SPEAKING

            for audio in self.tts_service.synthesize(res):
                self.speaker.play_audio(audio)

            self.state = State.IDLE

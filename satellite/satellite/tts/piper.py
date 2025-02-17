from pathlib import Path
from typing import Iterable

from piper.voice import PiperVoice

from ..debug import time_me
from .tts import TextToSpeechService


class PiperService(TextToSpeechService):
    model: PiperVoice

    def __init__(self, model_path: Path):
        self.model = PiperVoice.load(model_path)

        super().__init__()

    @time_me
    def synthesize(self, text: str) -> Iterable[bytes]:
        return self.model.synthesize_stream_raw(text)

from json import loads

import numpy as np
from vosk import KaldiRecognizer, Model, Path

from .asr import AutomaticSpeechRecognitionService


class VoskService(AutomaticSpeechRecognitionService):
    model: Model
    recognizer: KaldiRecognizer

    sample_rate = 16000

    def __init__(self, model_path: Path):
        self.model = Model(model_path=str(model_path))
        self.recognizer = KaldiRecognizer(self.model, self.sample_rate)

        super().__init__()

    def transcribe(self, audio: np.ndarray) -> str:
        if self.recognizer.AcceptWaveform(bytes(audio)):
            return loads(self.recognizer.Result())["text"]
        else:
            return loads(self.recognizer.PartialResult())["partial"]

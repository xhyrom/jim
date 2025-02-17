import numpy as np
from faster_whisper import WhisperModel

from .asr import AutomaticSpeechRecognitionService


class WhisperService(AutomaticSpeechRecognitionService):
    model: WhisperModel

    def __init__(self, model_path: str):
        self.model = WhisperModel(
            model_size_or_path=model_path, device="cpu", compute_type="int8"
        )

        super().__init__()

    def transcribe(self, audio: np.ndarray) -> str:
        segments, info = self.model.transcribe(
            audio, beam_size=5, language="en", condition_on_previous_text=False
        )

        return " ".join(segment.text for segment in segments)

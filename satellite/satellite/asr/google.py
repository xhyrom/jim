from typing import Optional

import numpy as np
from speech_recognition import AudioData, Recognizer

from ..debug import time_me
from .asr import AutomaticSpeechRecognitionService


class GoogleService(AutomaticSpeechRecognitionService):
    recognizer: Recognizer
    key: Optional[str]

    def __init__(self, key: Optional[str] = None) -> None:
        self.recognizer = Recognizer()
        self.key = key

        super().__init__()

    @time_me
    def transcribe(self, audio: np.ndarray) -> str:
        return self.recognizer.recognize_google(  # type: ignore
            AudioData(audio, 16000, 2), language="en-us", key=self.key
        )

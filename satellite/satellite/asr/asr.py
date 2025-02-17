from abc import ABC, abstractmethod

import numpy as np

from ..microphone import MicrophoneInput


class AutomaticSpeechRecognitionService(ABC):
    @abstractmethod
    def transcribe(self, audio: np.ndarray) -> str:
        pass

    def run(self, microphone: MicrophoneInput) -> str:
        return self.transcribe(microphone.get_audio_vad())

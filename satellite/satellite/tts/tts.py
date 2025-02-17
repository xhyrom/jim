from abc import ABC, abstractmethod
from typing import Iterable


class TextToSpeechService(ABC):
    @abstractmethod
    def synthesize(self, text: str) -> Iterable[bytes]:
        pass

    def run(self, text: str) -> Iterable[bytes]:
        return self.synthesize(text)

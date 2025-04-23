from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod


class NLUEngine(ABC):
    @abstractmethod
    def initialize(self, intents_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def parse(self, text: str) -> Dict[str, Any]:
        pass


from .pattern import PatternNLU

import logging
from abc import ABC, abstractmethod
from typing import List, Tuple

logger = logging.getLogger(__name__)


class LEDController(ABC):
    @abstractmethod
    def set_pixels(self, colors: List[Tuple[int, int, int]]) -> None:
        pass

    @abstractmethod
    def off(self) -> None:
        pass

    @abstractmethod
    def cleanup(self) -> None:
        pass

    @property
    @abstractmethod
    def pixel_count(self) -> int:
        pass


class MockLEDController(LEDController):
    def __init__(self, num_leds: int = 3):
        self._num_leds = num_leds
        self._pixels = [(0, 0, 0)] * num_leds
        logger.info(f"Mock LED controller initialized with {num_leds} LEDs")

    def set_pixels(self, colors: List[Tuple[int, int, int]]) -> None:
        self._pixels = colors[: self._num_leds]
        pixel_str = ", ".join(f"({r},{g},{b})" for r, g, b in self._pixels)
        logger.debug(f"Mock LEDs set to: [{pixel_str}]")

    def off(self) -> None:
        self._pixels = [(0, 0, 0)] * self._num_leds
        logger.debug("Mock LEDs turned off")

    def cleanup(self) -> None:
        self.off()

    @property
    def pixel_count(self) -> int:
        return self._num_leds

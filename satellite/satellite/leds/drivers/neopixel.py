import logging

from ..controller import LEDController

logger = logging.getLogger(__name__)


class NeoPixelController(LEDController):
    def __init__(self, pin: int = 18, num_leds: int = 10, brightness: float = 0.5): ...

    def set_pixels(self, colors: list[tuple[int, int, int]]) -> None: ...

    def off(self) -> None: ...

    def cleanup(self) -> None: ...

    @property
    def pixel_count(self) -> int: ...

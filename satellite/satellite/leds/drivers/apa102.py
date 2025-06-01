"""
Controller for APA102 LEDs (ReSpeaker Pi Hat)
"""

import logging

from ..controller import LEDController

logger = logging.getLogger(__name__)


class APAController(LEDController):
    def __init__(self, num_leds: int = 3, brightness: int = 10):
        try:
            from apa102_pi.driver import apa102

            self._driver = apa102.APA102(num_led=num_leds, global_brightness=brightness)
            self._num_leds = num_leds
            logger.info(f"APA102 controller initialized with {num_leds} LEDs")
        except ImportError:
            logger.warning(
                "apa102_pi module not found, APA102 controller not available"
            )
            self._driver = None
            self._num_leds = 0

    def set_pixels(self, colors: list[tuple[int, int, int]]) -> None:
        if not self._driver:
            return

        for i, (r, g, b) in enumerate(colors[: self._num_leds]):
            self._driver.set_pixel(i, r, g, b)
        self._driver.show()

    def off(self) -> None:
        if not self._driver:
            return

        for i in range(self._num_leds):
            self._driver.set_pixel(i, 0, 0, 0)
        self._driver.show()

    def cleanup(self) -> None:
        self.off()

    @property
    def pixel_count(self) -> int:
        return self._num_leds

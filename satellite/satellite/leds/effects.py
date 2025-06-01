import random
import time
from typing import Callable, Tuple

from .controller import LEDController

DEFAULT_FLICKER_RANGE = (0.85, 1.15)
THINK_FLICKER_RANGE = (0.7, 1.3)


class LanternEffects:
    @staticmethod
    def apply_color_with_brightness(
        controller: LEDController, base_color: Tuple[int, int, int], brightness: float
    ) -> None:
        r = min(255, int(base_color[0] * brightness))
        g = min(255, int(base_color[1] * brightness))
        b = min(255, int(base_color[2] * brightness))

        colors = [(r, g, b)] * controller.pixel_count
        controller.set_pixels(colors)

    @staticmethod
    def always_on(
        controller: LEDController,
        base_color: Tuple[int, int, int],
        should_stop: Callable[[], bool],
    ) -> None:
        while not should_stop():
            flicker = random.uniform(*DEFAULT_FLICKER_RANGE)
            LanternEffects.apply_color_with_brightness(controller, base_color, flicker)

            time.sleep(random.uniform(0.05, 0.2))

    @staticmethod
    def wakeup(
        controller: LEDController,
        base_color: Tuple[int, int, int],
    ) -> None:
        for i in range(10):
            brightness = 1.0 + (i / 10)
            LanternEffects.apply_color_with_brightness(
                controller, base_color, brightness
            )
            time.sleep(0.05)

    @staticmethod
    def listen(
        controller: LEDController,
        base_color: Tuple[int, int, int],
        should_stop: Callable[[], bool],
    ) -> None:
        brightness = 1.0
        step = 0.05

        while not should_stop():
            brightness += step
            if brightness >= 1.3 or brightness <= 0.7:
                step = -step

            LanternEffects.apply_color_with_brightness(
                controller, base_color, brightness
            )
            time.sleep(0.1)

    @staticmethod
    def think(
        controller: LEDController,
        base_color: Tuple[int, int, int],
        should_stop: Callable[[], bool],
    ) -> None:
        while not should_stop():
            flicker = random.uniform(*THINK_FLICKER_RANGE)
            LanternEffects.apply_color_with_brightness(controller, base_color, flicker)

            time.sleep(random.uniform(0.02, 0.1))

    @staticmethod
    def speak(
        controller: LEDController,
        base_color: Tuple[int, int, int],
        should_stop: Callable[[], bool],
    ) -> None:
        brightness = 1.0
        step = 0.1

        while not should_stop():
            brightness += step
            if brightness >= 1.2 or brightness <= 0.8:
                step = -step

            LanternEffects.apply_color_with_brightness(
                controller, base_color, brightness
            )
            time.sleep(0.05)

    @staticmethod
    def fade_off(
        controller: LEDController,
        base_color: Tuple[int, int, int],
    ) -> None:
        for i in range(10):
            brightness = 1.0 - (i / 10)
            LanternEffects.apply_color_with_brightness(
                controller, base_color, brightness
            )
            time.sleep(0.05)

        controller.off()

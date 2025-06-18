import logging

from ..controller import LEDController

logger = logging.getLogger(__name__)


class NeoPixelController(LEDController):
    def __init__(self, pin: int = 18, num_leds: int = 10, brightness: float = 0.5):
        try:
            import board
            import adafruit_pixelbuf
            from adafruit_raspberry_pi5_neopixel_write import neopixel_write

            pin_map = {
                18: board.D18,
            }

            board_pin = pin_map.get(pin, board.D18)

            class Pi5Pixelbuf(adafruit_pixelbuf.PixelBuf):
                def __init__(self, pin, size, **kwargs):
                    self._pin = pin
                    super().__init__(size=size, **kwargs)

                def _transmit(self, buf):
                    neopixel_write(self._pin, buf)

            self._pixels = Pi5Pixelbuf(
                board_pin,
                num_leds,
                auto_write=True,
            )
            self._num_leds = num_leds
            self._brightness = brightness
            if hasattr(self._pixels, "brightness"):
                self._pixels.brightness = brightness

            logger.info(f"NeoPixel controller initialized with {num_leds} LEDs")
        except ImportError as e:
            logger.warning(f"Error initializing NeoPixel controller: {e}")
            self._pixels = None
            self._num_leds = 0

    def set_pixels(self, colors: list[tuple[int, int, int]]) -> None:
        if not self._pixels:
            return

        for i, color in enumerate(colors[:self._num_leds]):
            self._pixels[i] = color

        if not getattr(self._pixels, "auto_write", True):
            self._pixels.show()

    def off(self) -> None:
        if not self._pixels:
            return

        for i in range(self._num_leds):
            self._pixels[i] = (0, 0, 0)

        if not getattr(self._pixels, "auto_write", True):
            self._pixels.show()

    def cleanup(self) -> None:
        self.off()

    @property
    def pixel_count(self) -> int:
        return self._num_leds

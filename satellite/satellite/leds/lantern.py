"""
Minecraft Lantern manager for controlling LED effects
"""

import importlib
import logging
import queue as Queue
import threading
from datetime import datetime
from typing import Optional

from ..config import LEDConfig, LEDDriverType
from .controller import LEDController, MockLEDController
from .drivers import APAController, NeoPixelController
from .effects import LanternEffects

logger = logging.getLogger(__name__)


class MinecraftLantern:
    """
    Minecraft lantern effect manager for LED strips
    Implements various lighting effects inspired by Minecraft lanterns
    """

    def __init__(self, config: Optional[LEDConfig] = None):
        """
        Initialize the lantern effect system

        Args:
            config: LED configuration options
        """
        self._config = config or LEDConfig()
        self._controller = self._create_controller()
        self._base_color = self._config.base_color

        # Set up the queue and thread for effects
        self._next = threading.Event()
        self._queue = Queue.Queue()
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()

        # Start with lantern glow effect if in active hours
        if self._is_active_time():
            self.lantern_glow()
        else:
            self.off()

    def _create_controller(self) -> LEDController:
        """Create an appropriate LED controller based on configuration"""

        if self._config.driver_type == LEDDriverType.AUTO:
            # Try to auto-detect available controllers
            try:
                # Try APA102 (ReSpeaker) first
                importlib.import_module("apa102_pi.driver.apa102")
                return APAController(
                    num_leds=self._config.num_leds, brightness=self._config.brightness
                )
            except ImportError:
                pass

            try:
                # Then try NeoPixel
                importlib.import_module("board")
                importlib.import_module("neopixel")
                return NeoPixelController(num_leds=self._config.num_leds)
            except ImportError:
                pass

            # Fall back to mock controller
            logger.warning("No LED controllers found, using mock controller")
            return MockLEDController(num_leds=self._config.num_leds)

        elif self._config.driver_type == LEDDriverType.APA102:
            return APAController(
                num_leds=self._config.num_leds, brightness=self._config.brightness
            )
        elif self._config.driver_type == LEDDriverType.NEOPIXEL:
            return NeoPixelController(num_leds=self._config.num_leds)
        else:
            return MockLEDController(num_leds=self._config.num_leds)

    def _is_active_time(self) -> bool:
        """Check if LEDs should be active based on schedule"""
        if not self._config.schedule.enabled:
            return True  # Always on if scheduling is disabled

        current_hour = datetime.now().hour
        start = self._config.schedule.start_hour
        end = self._config.schedule.end_hour

        # Handle wrapping around midnight
        if start <= end:
            return start <= current_hour < end
        else:
            return current_hour >= start or current_hour < end

    # Public API methods

    def lantern_glow(self) -> None:
        """Activate the lantern glow effect"""
        if not self._is_active_time():
            self.off()
            return

        self._next.set()
        self._queue.put(self._lantern_glow)

    def wakeup(self) -> None:
        """Brighten the lantern when woken up"""
        if not self._is_active_time():
            return

        self._next.set()
        self._queue.put(self._wakeup)

    def listen(self) -> None:
        """Subtle pulsing while listening"""
        if not self._is_active_time():
            return

        self._next.set()
        self._queue.put(self._listen)

    def think(self) -> None:
        """Faster flickering while thinking"""
        if not self._is_active_time():
            return

        self._next.set()
        self._queue.put(self._think)

    def speak(self) -> None:
        """Rhythmic pulsing while speaking"""
        if not self._is_active_time():
            return

        self._next.set()
        self._queue.put(self._speak)

    def off(self) -> None:
        """Turn off the lantern"""
        self._next.set()
        self._queue.put(self._off)

    def cleanup(self) -> None:
        """Clean up resources when shutting down"""
        self.off()
        self._controller.cleanup()

    def _run(self) -> None:
        """Main effect thread loop"""
        while True:
            func = self._queue.get()
            try:
                func()
            except Exception as e:
                logger.error(f"Error in LED effect: {e}")

    # Effect handler methods that use the effects library

    def _lantern_glow(self) -> None:
        """Default gentle flickering effect like a Minecraft lantern"""
        self._next.clear()
        LanternEffects.lantern_glow(
            self._controller, self._base_color, should_stop=lambda: self._next.is_set()
        )

    def _wakeup(self) -> None:
        """Brighten up when activated"""
        LanternEffects.wakeup(self._controller, self._base_color)
        self.lantern_glow()  # Return to normal glow

    def _listen(self) -> None:
        """Subtle pulsing while listening"""
        self._next.clear()
        LanternEffects.listen(
            self._controller, self._base_color, should_stop=lambda: self._next.is_set()
        )

    def _think(self) -> None:
        """Faster, more erratic flickering while thinking"""
        self._next.clear()
        LanternEffects.think(
            self._controller, self._base_color, should_stop=lambda: self._next.is_set()
        )

    def _speak(self) -> None:
        """Rhythmic pulsing while speaking"""
        self._next.clear()
        LanternEffects.speak(
            self._controller, self._base_color, should_stop=lambda: self._next.is_set()
        )

    def _off(self) -> None:
        """Fade out effect"""
        LanternEffects.fade_off(self._controller, self._base_color)

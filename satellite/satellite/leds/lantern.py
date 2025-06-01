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
    def __init__(self, config: Optional[LEDConfig] = None):
        self._config = config or LEDConfig()
        self._controller = self._create_controller()
        self._base_color = self._config.base_color

        self._next = threading.Event()
        self._queue = Queue.Queue()
        self._current_effect = None
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()

        self.always_on()

    def _create_controller(self) -> LEDController:
        if self._config.driver_type == LEDDriverType.AUTO:
            try:
                importlib.import_module("apa102_pi.driver.apa102")
                return APAController(
                    num_leds=self._config.num_leds, brightness=self._config.brightness
                )
            except ImportError:
                pass

            try:
                importlib.import_module("board")
                importlib.import_module("neopixel")
                return NeoPixelController(num_leds=self._config.num_leds)
            except ImportError:
                pass

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
        if not self._config.schedule.enabled:
            return True

        current_hour = datetime.now().hour
        start = self._config.schedule.start_hour
        end = self._config.schedule.end_hour

        if start <= end:
            return start <= current_hour < end
        else:
            return current_hour >= start or current_hour < end

    def always_on(self) -> None:
        self._clear_queue()
        self._queue.put(self._always_on)
        self._next.set()

    def wakeup(self) -> None:
        self._clear_queue()
        self._queue.put(self._wakeup)
        self._next.set()

    def listen(self) -> None:
        self._clear_queue()
        self._queue.put(self._listen)
        self._next.set()

    def think(self) -> None:
        self._clear_queue()
        self._queue.put(self._think)
        self._next.set()

    def speak(self) -> None:
        self._clear_queue()
        self._queue.put(self._speak)
        self._next.set()

    def off(self) -> None:
        self._clear_queue()
        self._queue.put(self._off)
        self._next.set()

    def _clear_queue(self) -> None:
        try:
            while True:
                self._queue.get_nowait()
                self._queue.task_done()
        except Queue.Empty:
            pass

    def cleanup(self) -> None:
        self.off()
        self._controller.cleanup()

    def _run(self) -> None:
        while True:
            try:
                func = self._queue.get()
                self._current_effect = func.__name__

                self._next.clear()

                try:
                    func()
                except Exception as e:
                    logger.error(f"Error in LED effect {func.__name__}: {e}")
                finally:
                    self._queue.task_done()
                    self._current_effect = None
            except Exception as e:
                logger.error(f"Error in LED thread: {e}")

    def _always_on(self) -> None:
        if not self._is_active_time():
            LanternEffects.fade_off(self._controller, self._base_color)
            return

        LanternEffects.always_on(
            self._controller, self._base_color, should_stop=lambda: self._next.is_set()
        )

    def _wakeup(self) -> None:
        LanternEffects.wakeup(self._controller, self._base_color)

    def _listen(self) -> None:
        LanternEffects.listen(
            self._controller, self._base_color, should_stop=lambda: self._next.is_set()
        )

    def _think(self) -> None:
        LanternEffects.think(
            self._controller, self._base_color, should_stop=lambda: self._next.is_set()
        )

    def _speak(self) -> None:
        LanternEffects.speak(
            self._controller, self._base_color, should_stop=lambda: self._next.is_set()
        )

    def _off(self) -> None:
        LanternEffects.fade_off(self._controller, self._base_color)

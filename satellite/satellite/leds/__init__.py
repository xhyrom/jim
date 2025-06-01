import logging
from typing import Optional

from ..config import LEDConfig
from .lantern import MinecraftLantern

logger = logging.getLogger(__name__)

try:
    lantern = None

    def initialize_lantern(config: Optional[LEDConfig] = None) -> MinecraftLantern:
        """Initialize the lantern with configuration"""
        global lantern
        if lantern is None:
            lantern = MinecraftLantern(config)
        return lantern

except Exception as e:
    logger.error(f"Failed to import LED modules: {e}")

    class DummyLantern:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None

    lantern = DummyLantern()

    def initialize_lantern(config: Optional[LEDConfig] = None) -> DummyLantern:
        return lantern


__all__ = ["initialize_lantern", "lantern"]

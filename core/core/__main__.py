import asyncio
from pathlib import Path

from .config import AppConfig
from .core import Core

_DIR = Path(__file__).parent
_CONFIG_PATH = _DIR / ".." / "config.toml"


async def main() -> None:
    print("Loading config...")
    config = AppConfig.from_file(_CONFIG_PATH)

    print("Starting core...")
    core = Core(config)

    task = asyncio.create_task(core.run(), name="core run")
    await task


def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run()

from pathlib import Path
import asyncio

from .core import Core
from .config import Config

_DIR = Path(__file__).parent
_CONFIG_PATH = _DIR / ".." / "config.json"


async def main() -> None:
    print("Loading config...")
    config = Config.from_file(_CONFIG_PATH)

    print("Starting Core...")
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

import asyncio

from .core import Core


async def main() -> None:
    core = Core()

    task = asyncio.create_task(core.run(), name="core run")
    await task


def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run()

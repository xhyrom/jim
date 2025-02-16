import asyncio

from .satellite import Satellite


async def main() -> None:
    print("Hello, World!")
    satellite = Satellite()

    task = asyncio.create_task(satellite.run(), name="satellite run")
    await task


def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run()

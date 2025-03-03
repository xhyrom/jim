import asyncio


async def main() -> None:
    print("Hello from core :)")


def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run()

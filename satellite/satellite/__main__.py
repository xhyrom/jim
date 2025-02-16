import asyncio


async def main() -> None:
    print("Hello, World!")


def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run()

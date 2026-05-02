import asyncio

from hypercorn.asyncio import Config, serve

from app import create_app

app = create_app()


async def main():
    config = Config()
    config.bind = ["0.0.0.0:9595"]

    await serve(app, config)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

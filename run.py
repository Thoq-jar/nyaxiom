import asyncio

from hypercorn.asyncio import Config, serve

from app import create_app, run_db_init

app = create_app()


async def main():
    await run_db_init(app)

    config = Config()
    config.bind = ["127.0.0.1:9595"]

    await serve(app, config)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

import quart_flask_patch  # noqa: F401
import os
import asyncio
import logging
from quart import Quart
from hypercorn.asyncio import serve
from hypercorn.config import Config
from src.db.db import db
from src.utils.misc.colors import ColorFormatter

logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)
logger.propagate = False

handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter())
logger.addHandler(handler)


async def run_db_init(app):
    async with app.app_context():
        from src.db.model import FetchTask

        logger.debug("Initializing DB...")
        db.create_all()
        task = FetchTask.query.filter_by(task_name="dashboard").first()
        if not task:
            db.session.add(FetchTask(task_name="dashboard", update_interval=3))
            db.session.commit()
        logger.info("DB initialized")


def create_app() -> Quart:
    app = Quart(__name__, template_folder="templates", static_url_path="/static")
    db_path = os.path.join(app.instance_path, "nyaxiom.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    from src.routes.api.routes import api_bp
    from src.routes.main.routes import main_bp

    logging.debug("Registering blueprints...")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(main_bp, url_prefix="/")

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)  # ty:ignore[invalid-argument-type]
    return app


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

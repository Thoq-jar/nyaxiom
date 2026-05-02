import asyncio
import logging
import os

import quart_flask_patch  # noqa: F401
from quart import Quart

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
        from src.db.model import FetchTask, SearchEngine, ShowWeather

        logger.debug("Initializing DB...")
        db.create_all()
        fetch_task = FetchTask.query.filter_by(task_name="dashboard").first()
        if not fetch_task:
            logger.debug("not fetch_task")
            db.session.add(FetchTask(task_name="dashboard"))
            db.session.commit()

        show_weather = ShowWeather.query.filter_by(task_name="dashboard").first()
        if not show_weather:
            logger.debug("not show_weather")
            db.session.add(ShowWeather(task_name="dashboard"))
            db.session.commit()

        search_engine = SearchEngine.query.filter_by(task_name="dashboard").first()
        if not search_engine:
            logger.debug("not search_engine")
            db.session.add(SearchEngine(task_name="dashboard"))
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
asyncio.run(run_db_init(app))

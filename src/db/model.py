from src.db.db import db
from src.mixin.configurable_interval import ConfigurableIntervalMixin
from src.mixin.show_weather import ShowWeatherMixin


class FetchTask(db.Model, ConfigurableIntervalMixin):  # ty:ignore[unsupported-base]
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(100), unique=True)
    last_run = db.Column(db.DateTime, default=db.func.now())


class ShowWeather(db.Model, ShowWeatherMixin):  # ty:ignore[unsupported-base]
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(101), unique=True)
    last_run = db.Column(db.DateTime, default=db.func.now())

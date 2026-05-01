from src.db.db import db
from src.mixin.configurable_interval import ConfigurableIntervalMixin


class FetchTask(db.Model, ConfigurableIntervalMixin):  # ty:ignore[unsupported-base]
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(100), unique=True)
    last_run = db.Column(db.DateTime, default=db.func.now())

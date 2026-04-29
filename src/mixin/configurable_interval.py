from sqlalchemy.ext.declarative import declared_attr
from src.db.db import db


class ConfigurableIntervalMixin:
    @declared_attr
    def update_interval(cls):
        return db.Column(
            db.Integer,
            default=2,
            nullable=False,
            info={"label": "Update Interval (seconds)"},
        )

    def is_due(self, last_updated):
        from datetime import datetime, timezone

        delta = (datetime.now(timezone.utc) - last_updated).total_seconds()
        return delta >= self.update_interval

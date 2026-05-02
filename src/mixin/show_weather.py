from sqlalchemy.ext.declarative import declared_attr

from src.db.db import db


class ShowWeatherMixin:
    @declared_attr
    def checked(cls):
        return db.Column(
            db.Integer,
            default=True,
            nullable=False,
            info={"label": "Show Weather (IP-Based)"},
        )

    def is_due(self, last_updated):
        from datetime import datetime, timezone

        delta = (datetime.now(timezone.utc) - last_updated).total_seconds()
        return delta >= self.checked

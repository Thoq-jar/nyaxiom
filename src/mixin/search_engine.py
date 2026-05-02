from sqlalchemy.ext.declarative import declared_attr

from src.db.db import db


class SearchEngineMixin:
    @declared_attr
    def engine(cls):
        return db.Column(
            db.Integer,
            default="https://startpage.com/search?q=%s",
            nullable=False,
            info={"label": "Search Engine"},
        )

    def is_due(self, last_updated):
        from datetime import datetime, timezone

        delta = (datetime.now(timezone.utc) - last_updated).total_seconds()
        return delta >= self.engine

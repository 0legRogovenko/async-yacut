"""Модели базы данных."""
from datetime import datetime

from yacut import db


class URLMap(db.Model):
    """Соответствие короткого идентификатора оригинальной ссылке."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(256), nullable=False)
    short = db.Column(db.String(16), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

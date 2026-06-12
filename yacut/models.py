"""Модели базы данных."""
import re
from datetime import datetime
from random import choices

from flask import url_for

from yacut import db
from .constants import (
    MAX_ORIGINAL_LENGTH,
    MAX_SHORT_GENERATION_ATTEMPTS,
    MAX_SHORT_LENGTH,
    REDIRECT_VIEW_ENDPOINT,
    RESERVED_SHORTS,
    SHORT_CHARS,
    SHORT_LENGTH,
    SHORT_PATTERN,
)

DUPLICATE_SHORT_MESSAGE = (
    'Предложенный вариант короткой ссылки уже существует.'
)
INVALID_SHORT_MESSAGE = 'Указано недопустимое имя для короткой ссылки'
SHORT_GENERATION_ERROR_MESSAGE = (
    'Не удалось сгенерировать уникальный короткий идентификатор '
    'за {} попыток.'
)


class URLMap(db.Model):
    """Соответствие короткого идентификатора оригинальной ссылке."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_ORIGINAL_LENGTH), nullable=False)
    short = db.Column(db.String(MAX_SHORT_LENGTH), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @staticmethod
    def get(short):
        """Возвращает запись по короткому идентификатору или None."""
        return URLMap.query.filter_by(short=short).first()

    @staticmethod
    def is_available(short):
        """Проверяет, что идентификатор свободен и не зарезервирован."""
        return short not in RESERVED_SHORTS and URLMap.get(short) is None

    @staticmethod
    def generate_short():
        """Генерирует свободный случайный короткий идентификатор."""
        for _ in range(MAX_SHORT_GENERATION_ATTEMPTS):
            short = ''.join(choices(SHORT_CHARS, k=SHORT_LENGTH))
            if URLMap.is_available(short):
                return short
        raise RuntimeError(
            SHORT_GENERATION_ERROR_MESSAGE.format(
                MAX_SHORT_GENERATION_ATTEMPTS
            )
        )

    @staticmethod
    def create(original, short=None):
        """Создаёт и сохраняет запись, при необходимости генерируя short."""
        if short:
            if (
                len(short) > MAX_SHORT_LENGTH
                or not re.fullmatch(SHORT_PATTERN, short)
            ):
                raise ValueError(INVALID_SHORT_MESSAGE)
            if not URLMap.is_available(short):
                raise ValueError(DUPLICATE_SHORT_MESSAGE)
        else:
            short = URLMap.generate_short()
        url_map = URLMap(original=original, short=short)
        db.session.add(url_map)
        db.session.commit()
        return url_map

    def to_short_url(self):
        """Возвращает абсолютный урл короткой ссылки."""
        return url_for(
            REDIRECT_VIEW_ENDPOINT, short=self.short, _external=True
        )

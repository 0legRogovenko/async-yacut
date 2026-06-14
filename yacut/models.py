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
    RESERVED_SHORTS,
    SHORT_CHARS,
    SHORT_LENGTH,
    SHORT_PATTERN,
)

INVALID_ORIGINAL_MESSAGE = (
    'Указанная ссылка превышает максимальную длину '
    f'({MAX_ORIGINAL_LENGTH} символов).'
)
INVALID_SHORT_MESSAGE = 'Указано недопустимое имя для короткой ссылки'
DUPLICATE_SHORT_MESSAGE = (
    'Предложенный вариант короткой ссылки уже существует.'
)
SHORT_GENERATION_ERROR_MESSAGE = (
    'Не удалось сгенерировать уникальный короткий идентификатор. '
    f'Превышено максимальное число попыток ({MAX_SHORT_GENERATION_ATTEMPTS}).'
)


class URLMapError(Exception):
    """Базовая ошибка операций с моделью URLMap."""


class InvalidOriginalError(URLMapError):
    """Указана недопустимая оригинальная ссылка."""


class InvalidShortError(URLMapError):
    """Указан недопустимый короткий идентификатор."""


class DuplicateShortError(URLMapError):
    """Короткий идентификатор уже занят или зарезервирован."""


class ShortGenerationError(URLMapError):
    """Не удалось сгенерировать уникальный короткий идентификатор."""


class URLMap(db.Model):
    """Модель коротких ссылок с методами для их создания и поиска."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_ORIGINAL_LENGTH), nullable=False)
    short = db.Column(db.String(MAX_SHORT_LENGTH), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @staticmethod
    def get(short):
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
        raise ShortGenerationError(SHORT_GENERATION_ERROR_MESSAGE)

    @staticmethod
    def create(original, short=None, validate_short=True,
               validate_original=True, commit=True):
        """Создаёт и сохраняет запись, при необходимости генерируя short.

        Параметры `validate_short` и `validate_original` позволяют
        пропустить проверку формата, если она уже выполнена формой.
        Если `commit` равен False, запись добавляется в сессию без
        сохранения - для пакетного создания записей одним коммитом.
        """
        if validate_original and len(original) > MAX_ORIGINAL_LENGTH:
            raise InvalidOriginalError(INVALID_ORIGINAL_MESSAGE)
        if short:
            if validate_short and (
                len(short) > MAX_SHORT_LENGTH
                or not re.fullmatch(SHORT_PATTERN, short)
            ):
                raise InvalidShortError(INVALID_SHORT_MESSAGE)
            if not URLMap.is_available(short):
                raise DuplicateShortError(DUPLICATE_SHORT_MESSAGE)
        else:
            short = URLMap.generate_short()
        url_map = URLMap(original=original, short=short)
        db.session.add(url_map)
        if commit:
            db.session.commit()
        return url_map

    def to_short_url(self, endpoint):
        """Возвращает абсолютный урл короткой ссылки для указанной ручки."""
        return url_for(endpoint, short=self.short, _external=True)

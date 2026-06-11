"""Вспомогательные функции, общие для views и api_views."""
from random import randrange

from .constants import LINK_CHARS, LINK_LENGTH
from .models import URLMap


def get_unique_short_id():
    """Генерация уникального короткого идентификатора"""
    while True:
        short_id = ''.join(LINK_CHARS[randrange(len(LINK_CHARS))]
                           for _ in range(LINK_LENGTH))

        if not URLMap.query.filter_by(short=short_id).first():
            return short_id

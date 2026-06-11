"""REST API для создания и получения коротких ссылок."""
import re

from flask import jsonify, request, url_for

from . import app, db
from .constants import (
    CUSTOM_ID_PATTERN,
    DUPLICATE_ID_MESSAGE,
    INVALID_ID_MESSAGE,
    MAX_CUSTOM_ID_LENGTH,
    RESERVED_SHORT_IDS,
)
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .utils import get_unique_short_id


@app.route('/api/id/', methods=['POST'])
def api_create_id():
    """Создание короткой ссылки через REST API"""
    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')

    custom_id = data.get('custom_id')
    if custom_id:
        if (
            len(custom_id) > MAX_CUSTOM_ID_LENGTH
            or not re.fullmatch(CUSTOM_ID_PATTERN, custom_id)
            or custom_id in RESERVED_SHORT_IDS
        ):
            raise InvalidAPIUsage(INVALID_ID_MESSAGE)
        if URLMap.query.filter_by(short=custom_id).first():
            raise InvalidAPIUsage(DUPLICATE_ID_MESSAGE)
    else:
        custom_id = get_unique_short_id()

    url_map = URLMap(original=data['url'], short=custom_id)
    db.session.add(url_map)
    db.session.commit()
    return jsonify({
        'url': url_map.original,
        'short_link': url_for(
            'redirect_view', short_id=url_map.short, _external=True
        )
    }), 201


@app.route('/api/id/<short_id>/', methods=['GET'])
def api_get_url(short_id):
    """Получение оригинальной ссылки по короткому идентификатору"""
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', 404)
    return jsonify({'url': url_map.original})

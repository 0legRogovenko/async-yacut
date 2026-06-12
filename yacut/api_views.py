"""REST API для создания и получения коротких ссылок."""
from http import HTTPStatus

from flask import jsonify, request

from . import app
from .error_handlers import InvalidAPIUsage
from .models import URLMap

EMPTY_BODY_MESSAGE = 'Отсутствует тело запроса'
URL_REQUIRED_MESSAGE = '"url" является обязательным полем!'
SHORT_NOT_FOUND_MESSAGE = 'Указанный id не найден'


@app.route('/api/id/', methods=['POST'])
def api_create_id():
    """Создание короткой ссылки через REST API."""
    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage(EMPTY_BODY_MESSAGE)
    if 'url' not in data:
        raise InvalidAPIUsage(URL_REQUIRED_MESSAGE)
    try:
        url_map = URLMap.create(
            original=data['url'], short=data.get('custom_id')
        )
    except ValueError as error:
        raise InvalidAPIUsage(str(error))
    return jsonify({
        'url': url_map.original,
        'short_link': url_map.to_short_url(),
    }), HTTPStatus.CREATED


@app.route('/api/id/<short>/', methods=['GET'])
def api_get_url(short):
    """Получение оригинальной ссылки по короткому идентификатору."""
    url_map = URLMap.get(short)
    if url_map is None:
        raise InvalidAPIUsage(SHORT_NOT_FOUND_MESSAGE, HTTPStatus.NOT_FOUND)
    return jsonify({'url': url_map.original})

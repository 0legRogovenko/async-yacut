"""REST API для создания и получения коротких ссылок."""
from http import HTTPStatus

from flask import jsonify, request

from . import app
from .constants import REDIRECT_VIEW_ENDPOINT
from .error_handlers import InvalidAPIUsage
from .models import URLMap, URLMapError

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
        short_link = URLMap.create(
            original=data['url'], short=data.get('custom_id')
        ).to_short_url(REDIRECT_VIEW_ENDPOINT)
    except URLMapError as error:
        raise InvalidAPIUsage(str(error))
    return jsonify({
        'url': data['url'],
        'short_link': short_link,
    }), HTTPStatus.CREATED


@app.route('/api/id/<short>/', methods=['GET'])
def api_get_url(short):
    """Получение оригинальной ссылки по короткому идентификатору."""
    if (url_map := URLMap.get(short)) is None:
        raise InvalidAPIUsage(SHORT_NOT_FOUND_MESSAGE, HTTPStatus.NOT_FOUND)
    return jsonify({'url': url_map.original})

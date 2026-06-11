"""Обработчики ошибок для пользовательского интерфейса и API."""
from flask import jsonify, render_template

from . import app


class InvalidAPIUsage(Exception):
    """Ошибка API с сообщением и HTTP-статус-кодом ответа."""

    status_code = 400

    def __init__(self, message, status_code=None):
        """Сохраняет сообщение и (опционально) статус-код ошибки."""
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        """Возвращает данные ошибки в виде словаря для JSON-ответа."""
        return {'message': self.message}


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(error):
    """Преобразует InvalidAPIUsage в JSON-ответ с нужным статус-кодом."""
    return jsonify(error.to_dict()), error.status_code


@app.errorhandler(404)
def page_not_found(error):
    """Отображает страницу 404 для несуществующих маршрутов."""
    return render_template('404.html'), 404

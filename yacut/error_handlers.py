"""Обработчики ошибок для пользовательского интерфейса и API."""
from http import HTTPStatus

from flask import jsonify, render_template

from . import app, db


class InvalidAPIUsage(Exception):
    """Ошибка API с сообщением и HTTP-статус-кодом ответа."""

    def __init__(self, message, status_code=HTTPStatus.BAD_REQUEST):
        """Сохраняет сообщение и статус-код ошибки."""
        super().__init__()
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        """Возвращает данные ошибки в виде словаря для JSON-ответа."""
        return {'message': self.message}


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(error):
    """Преобразует InvalidAPIUsage в JSON-ответ с нужным статус-кодом."""
    return jsonify(error.to_dict()), error.status_code


@app.errorhandler(HTTPStatus.NOT_FOUND)
def page_not_found(error):
    """Отображает страницу 404 для несуществующих маршрутов."""
    return render_template('404.html'), HTTPStatus.NOT_FOUND


@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """Откатывает незавершённую транзакцию и отображает страницу 500."""
    db.session.rollback()
    return render_template('500.html'), HTTPStatus.INTERNAL_SERVER_ERROR

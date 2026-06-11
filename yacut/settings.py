"""Конфигурация Flask-приложения на основе переменных окружения."""
import os


class Config(object):
    """Настройки приложения: база данных, секретный ключ, токен Я.Диска."""

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')
    YANDEX_TOKEN = os.getenv('DISK_TOKEN')

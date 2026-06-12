"""Конфигурация Flask-приложения на основе переменных окружения."""
import os


class Config(object):
    """Настройки приложения: база данных, секретный ключ, токен Я.Диска."""

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///db.sqlite3')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    YANDEX_TOKEN = os.getenv('DISK_TOKEN')
    # Папка приложения на Яндекс Диске, в которую загружаются файлы
    DISK_APP_FOLDER = 'YaCut'
    # Расширения файлов, разрешённые для загрузки на Яндекс Диск
    ALLOWED_EXTENSIONS = ('jpg', 'jpeg', 'png', 'gif', 'bmp')

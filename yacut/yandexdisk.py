"""Асинхронная загрузка файлов на Яндекс Диск через aiohttp."""
import aiohttp
import asyncio

from . import app

# API Endpoints Яндекс Диска
API_HOST = 'https://cloud-api.yandex.net/v1/disk/resources'
GET_UPLOAD_LINK_URL = f'{API_HOST}/upload'
GET_DOWNLOAD_LINK_URL = f'{API_HOST}/download'

# Путь к папке приложения на Яндекс Диске.
# Префикс `app:` обязателен для токенов с правом
# "Доступ к папке приложения на Диске" (cloud_api:disk.app_folder).
DISK_FOLDER_PATH = 'app:/YaCut'


def get_auth_headers(token):
    """Возвращает заголовок авторизации"""
    return {'Authorization': f'OAuth {token}'}


async def ensure_disk_folder_exists(session, headers):
    """Создаёт папку приложения на Яндекс Диске, если её ещё нет"""
    async with session.put(
        API_HOST,
        headers=headers,
        params={'path': DISK_FOLDER_PATH}
    ):
        pass


async def async_upload_file_to_yandex_disk(images):
    """Асинхронная загрузка файлов на Яндекс Диск"""
    token = app.config.get('YANDEX_TOKEN')
    headers = get_auth_headers(token)
    tasks = []

    async with aiohttp.ClientSession() as session:
        await ensure_disk_folder_exists(session, headers)
        for image in images:
            tasks.append(
                asyncio.ensure_future(
                    upload_file_and_get_url(session, headers, image))
            )
        urls = await asyncio.gather(*tasks)

    return urls


async def upload_file_and_get_url(session, headers, image):
    """Загрузка файла на Яндекс Диск и получение ссылки для скачивания"""
    file_path = f'{DISK_FOLDER_PATH}/{image.filename}'

    # Шаг 1: Получить ссылку для загрузки файла
    async with session.get(
        GET_UPLOAD_LINK_URL,
        headers=headers,
        params={'path': file_path, 'overwrite': 'true'}
    ) as response:
        upload_data = await response.json()
        upload_url = upload_data['href']

    # Шаг 2: Загрузить файл на Яндекс Диск
    file_content = image.read()
    async with session.put(upload_url, data=file_content):
        pass

    # Шаг 3: Получить ссылку для скачивания файла
    async with session.get(
        GET_DOWNLOAD_LINK_URL,
        headers=headers,
        params={'path': file_path}
    ) as response:
        download_data = await response.json()
        download_url = download_data['href']

    return download_url

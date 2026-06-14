"""Асинхронная загрузка файлов на Яндекс Диск через aiohttp."""
import asyncio

import aiohttp

from . import app

# API Endpoints Яндекс Диска
API_HOST = 'https://cloud-api.yandex.net/v1/disk/resources'
GET_UPLOAD_LINK_URL = f'{API_HOST}/upload'
GET_DOWNLOAD_LINK_URL = f'{API_HOST}/download'

# Путь к папке приложения на Яндекс Диске.
# Префикс `app:` обязателен для токенов с правом
# "Доступ к папке приложения на Диске" (cloud_api:disk.app_folder).
DISK_FOLDER_PATH = 'app:/{}'.format(app.config['DISK_APP_FOLDER'])

AUTH_HEADERS = {'Authorization': f'OAuth {app.config["YANDEX_TOKEN"]}'}


async def ensure_disk_folder_exists(session):
    """Создаёт папку приложения на Яндекс Диске, если её ещё нет."""
    async with session.put(
        API_HOST,
        headers=AUTH_HEADERS,
        params={'path': DISK_FOLDER_PATH}
    ):
        pass


async def async_upload_files_to_yandex_disk(images):
    """Асинхронная загрузка файлов на Яндекс Диск."""
    async with aiohttp.ClientSession() as session:
        await ensure_disk_folder_exists(session)
        return await asyncio.gather(
            *(upload_file_and_get_url(session, image) for image in images)
        )


async def upload_file_and_get_url(session, image):
    """Загрузка файла на Яндекс Диск и получение ссылки для скачивания."""
    file_path = f'{DISK_FOLDER_PATH}/{image.filename}'

    async with session.get(
        GET_UPLOAD_LINK_URL,
        headers=AUTH_HEADERS,
        params={'path': file_path, 'overwrite': 'true'}
    ) as response:
        upload_url = (await response.json())['href']

    async with session.put(upload_url, data=image.read()):
        pass

    async with session.get(
        GET_DOWNLOAD_LINK_URL,
        headers=AUTH_HEADERS,
        params={'path': file_path}
    ) as response:
        return (await response.json())['href']

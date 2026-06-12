"""View-функции главной страницы, страницы загрузки файлов и редиректа."""
from http import HTTPStatus

import aiohttp
from flask import abort, flash, redirect, render_template

from . import app
from .forms import ImageMapForm, URLMapForm
from .models import URLMap
from .yandexdisk import async_upload_file_to_yandex_disk

UPLOAD_ERROR_MESSAGE = 'Не удалось загрузить файлы на Яндекс Диск.'


@app.route('/', methods=['GET', 'POST'])
def index_view():
    """Главная страница с формой для создания короткой ссылки."""
    form = URLMapForm()
    if not form.validate_on_submit():
        return render_template('index.html', form=form)

    try:
        url_map = URLMap.create(
            original=form.original_link.data, short=form.custom_id.data
        )
    except ValueError as error:
        flash(str(error))
        return render_template('index.html', form=form)

    return render_template(
        'index.html', form=form, short_link=url_map.to_short_url()
    )


@app.route('/<short>')
def redirect_view(short):
    """Перенаправление по короткой ссылке."""
    url_map = URLMap.get(short)
    if url_map is None:
        abort(HTTPStatus.NOT_FOUND)
    return redirect(url_map.original, code=HTTPStatus.FOUND)


@app.route('/files', methods=['GET', 'POST'])
async def file_upload_view():
    """Загрузка файлов на Яндекс Диск с получением коротких ссылок."""
    form = ImageMapForm()
    if not form.validate_on_submit():
        return render_template('file_upload.html', form=form)

    images = form.files.data
    try:
        urls = await async_upload_file_to_yandex_disk(images)
        files = [
            {
                'name': image.filename,
                'link': URLMap.create(original=url).to_short_url(),
            }
            for image, url in zip(images, urls)
        ]
    except aiohttp.ClientError:
        flash(UPLOAD_ERROR_MESSAGE)
        return render_template('file_upload.html', form=form)

    return render_template('file_upload.html', form=form, files=files)

"""View-функции главной страницы, страницы загрузки файлов и редиректа."""
from http import HTTPStatus

from flask import abort, flash, redirect, render_template

from . import app
from .constants import REDIRECT_VIEW_ENDPOINT
from .forms import ImageMapForm, URLMapForm
from .models import URLMap
from .yandexdisk import async_upload_files_to_yandex_disk

UPLOAD_ERROR_MESSAGE = 'Не удалось загрузить файлы на Яндекс Диск.'


@app.route('/', methods=['GET', 'POST'])
def index_view():
    """Главная страница с формой для создания короткой ссылки."""
    form = URLMapForm()
    if not form.validate_on_submit():
        return render_template('index.html', form=form)

    try:
        return render_template(
            'index.html',
            form=form,
            short_link=URLMap.create(
                original=form.original_link.data,
                short=form.custom_id.data,
                validate_short=False,
                validate_original=False,
            ).to_short_url(),
        )
    except URLMap.Error as error:
        flash(str(error))
        return render_template('index.html', form=form)


@app.route('/<short>', endpoint=REDIRECT_VIEW_ENDPOINT)
def redirect_view(short):
    """Перенаправление по короткой ссылке."""
    if (url_map := URLMap.get(short)) is None:
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
        urls = await async_upload_files_to_yandex_disk(images)
    except Exception as error:
        flash('{} {}'.format(UPLOAD_ERROR_MESSAGE, error))
        return render_template('file_upload.html', form=form)

    try:
        return render_template(
            'file_upload.html',
            form=form,
            files=[
                {
                    'name': image.filename,
                    'link': URLMap.create(
                        original=url,
                        commit=(i == len(images) - 1),
                    ).to_short_url(),
                }
                for i, (image, url) in enumerate(zip(images, urls))
            ],
        )
    except URLMap.Error as error:
        flash(str(error))
        return render_template('file_upload.html', form=form)

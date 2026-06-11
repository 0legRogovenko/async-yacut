"""View-функции главной страницы, страницы загрузки файлов и редиректа."""
from flask import abort, flash, redirect, render_template, url_for

from . import app, db
from .constants import DUPLICATE_ID_MESSAGE, RESERVED_SHORT_IDS
from .forms import ImageMapForm, URLMapForm
from .models import URLMap
from .utils import get_unique_short_id
from .yandexdisk import async_upload_file_to_yandex_disk


@app.route('/', methods=['GET', 'POST'])
def index_view():
    """Главная страница с формой для создания короткой ссылки"""
    form = URLMapForm()

    if form.validate_on_submit():
        original_link = form.original_link.data
        custom_id = form.custom_id.data

        if not custom_id:
            short_id = get_unique_short_id()
        elif custom_id in RESERVED_SHORT_IDS or URLMap.query.filter_by(
                short=custom_id).first():
            flash(DUPLICATE_ID_MESSAGE)
            return render_template('index.html', form=form)
        else:
            short_id = custom_id

        url_map = URLMap(original=original_link, short=short_id)
        db.session.add(url_map)
        db.session.commit()
        return render_template(
            'index.html',
            form=form,
            short_link=url_for(
                'redirect_view', short_id=short_id, _external=True
            )
        )

    return render_template('index.html', form=form)


@app.route('/<short_id>')
def redirect_view(short_id):
    """Перенаправление по короткой ссылке"""
    url_map = URLMap.query.filter_by(short=short_id).first()

    if url_map is None:
        abort(404)

    return redirect(url_map.original, code=302)


@app.route('/files', methods=['GET', 'POST'])
async def file_upload_view():
    """Загрузка файлов на Яндекс Диск с получением коротких ссылок"""
    form = ImageMapForm()

    if form.validate_on_submit():
        images = form.files.data
        urls = await async_upload_file_to_yandex_disk(images)

        files = []
        for image, url in zip(images, urls):
            short_id = get_unique_short_id()
            db.session.add(URLMap(original=url, short=short_id))
            files.append({
                'name': image.filename,
                'link': url_for(
                    'redirect_view', short_id=short_id, _external=True
                )
            })
        db.session.commit()
        return render_template('file_upload.html', form=form, files=files)

    return render_template('file_upload.html', form=form)

"""Формы для главной страницы и страницы загрузки файлов."""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp
from flask_wtf.file import FileAllowed, MultipleFileField

from .constants import (
    CUSTOM_ID_PATTERN, INVALID_ID_MESSAGE, MAX_CUSTOM_ID_LENGTH
)


class URLMapForm(FlaskForm):
    """Форма создания короткой ссылки на главной странице."""

    original_link = StringField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле'),
                    Length(1, 256)]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Optional(),
            Length(max=MAX_CUSTOM_ID_LENGTH),
            Regexp(CUSTOM_ID_PATTERN, message=INVALID_ID_MESSAGE),
        ]
    )
    submit = SubmitField('Создать')


class ImageMapForm(FlaskForm):
    """Форма загрузки файлов на странице /files."""

    files = MultipleFileField(
        'Выбрать файл',
        validators=[
            FileAllowed(
                ['jpg', 'jpeg', 'png', 'gif', 'bmp'],
                message=('Файл не выбран')
            )
        ]
    )
    submit = SubmitField('Загрузить')
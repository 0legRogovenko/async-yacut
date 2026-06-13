"""Формы для главной страницы и страницы загрузки файлов."""
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from .constants import MAX_ORIGINAL_LENGTH, MAX_SHORT_LENGTH, SHORT_PATTERN
from .models import INVALID_SHORT_MESSAGE
from .settings import Config

ORIGINAL_LINK_LABEL = 'Длинная ссылка'
ORIGINAL_LINK_REQUIRED_MESSAGE = 'Обязательное поле'
CUSTOM_ID_LABEL = 'Ваш вариант короткой ссылки'
CREATE_BUTTON_LABEL = 'Создать'
FILES_LABEL = 'Выбрать файл'
UPLOAD_BUTTON_LABEL = 'Загрузить'
ALLOWED_EXTENSIONS_MESSAGE = 'Допустимые расширения файлов: {}'.format(
    ', '.join(Config.ALLOWED_EXTENSIONS)
)


class URLMapForm(FlaskForm):
    """Форма создания короткой ссылки на главной странице."""

    original_link = URLField(
        ORIGINAL_LINK_LABEL,
        validators=[
            DataRequired(message=ORIGINAL_LINK_REQUIRED_MESSAGE),
            Length(max=MAX_ORIGINAL_LENGTH),
        ]
    )
    custom_id = StringField(
        CUSTOM_ID_LABEL,
        validators=[
            Optional(),
            Length(max=MAX_SHORT_LENGTH),
            Regexp(SHORT_PATTERN, message=INVALID_SHORT_MESSAGE),
        ]
    )
    submit = SubmitField(CREATE_BUTTON_LABEL)


class ImageMapForm(FlaskForm):
    """Форма загрузки файлов на странице /files."""

    files = MultipleFileField(
        FILES_LABEL,
        validators=[
            FileAllowed(
                Config.ALLOWED_EXTENSIONS,
                message=ALLOWED_EXTENSIONS_MESSAGE,
            )
        ]
    )
    submit = SubmitField(UPLOAD_BUTTON_LABEL)

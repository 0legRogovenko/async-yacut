# YaCut — сервис сокращения ссылок

YaCut позволяет превращать длинные ссылки в короткие и делиться ими.
Дополнительно сервис умеет асинхронно загружать файлы на Яндекс Диск
и выдавать короткие ссылки для их скачивания.

## Возможности

- Создание короткой ссылки автоматически (6 случайных символов) или по
  пользовательскому варианту (до 16 символов, латиница и цифры).
- Переадресация по короткой ссылке на оригинальный адрес.
- Загрузка нескольких файлов одновременно на Яндекс Диск с генерацией
  короткой ссылки на скачивание для каждого файла (асинхронно, через
  `aiohttp`).
- REST API для создания и получения коротких ссылок.
- Собственные обработчики ошибок для интерфейса (страница 404) и API
  (JSON-ответы с описанием ошибки).

## Технологии

- Python 3.12, Flask
- Flask-SQLAlchemy, Flask-Migrate (Alembic), SQLite
- Flask-WTF (формы и CSRF)
- aiohttp + asgiref (асинхронная загрузка файлов на Яндекс Диск)
- pytest, pytest-asyncio, pytest-aiohttp, flake8

## Структура проекта

```
yacut/
├── __init__.py        # инициализация приложения, БД, миграций
├── settings.py        # конфигурация из переменных окружения
├── constants.py        # константы проекта
├── models.py           # модель URLMap (микро-ORM)
├── forms.py             # формы URLMapForm и ImageMapForm
├── views.py             # главная страница, /files, редирект
├── api_views.py         # REST API (/api/id/...)
├── error_handlers.py    # обработчики ошибок UI и API
├── yandexdisk.py         # асинхронная загрузка на Яндекс Диск
├── static/                # CSS, JS, изображения
└── templates/             # base.html, includes, страницы
migrations/                # миграции Alembic
tests/                      # тесты
openapi.yml                 # спецификация API
postman_collection/         # коллекция запросов для Postman
```

## Установка и запуск

Клонировать репозиторий и перейти в него:

```bash
git clone https://github.com/0legRogovenko/async-yacut.git
cd async-yacut
```

Создать и активировать виртуальное окружение:

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate       # Windows
```

Установить зависимости:

```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

Создать файл `.env` на основе `.env.example` и заполнить переменные:

```
FLASK_APP=yacut
FLASK_ENV=development
SECRET_KEY=<случайная строка>
DATABASE_URI=sqlite:///db.sqlite3
DISK_TOKEN=<OAuth-токен Яндекс Диска>
```

`DISK_TOKEN` нужен для загрузки файлов на Яндекс Диск. Получить токен
можно, создав приложение на
[oauth.yandex.ru](https://oauth.yandex.ru/) с правами «Яндекс.Диск REST
API»: «Доступ к папке приложения на Диске» и «Доступ к информации о
Диске». При таких правах файлы сохраняются в папку `app:/YaCut`
(папка приложения на Диске), которую сервис создаёт автоматически.

Применить миграции:

```bash
flask db upgrade
```

Запустить проект:

```bash
flask run
```

Главная страница доступна на
[http://127.0.0.1:5000/](http://127.0.0.1:5000/), страница загрузки
файлов — на [http://127.0.0.1:5000/files](http://127.0.0.1:5000/files).

## Тестирование

```bash
pytest
flake8
```

## API

API доступен без авторизации и состоит из двух эндпоинтов. Полная
спецификация — в [openapi.yml](openapi.yml) (можно открыть в
[Swagger Editor](https://editor.swagger.io/)). Готовые запросы для
отладки — в [postman_collection](postman_collection).

### Создать короткую ссылку

```
POST /api/id/
Content-Type: application/json

{
  "url": "https://practicum.yandex.ru",
  "custom_id": "myshorturl"
}
```

`custom_id` — необязательное поле (до 16 символов, латиница и цифры).
Если не указан, генерируется автоматически.

Ответ `201 Created`:

```json
{
  "url": "https://practicum.yandex.ru",
  "short_link": "http://127.0.0.1:5000/myshorturl"
}
```

### Получить оригинальную ссылку

```
GET /api/id/<short>/
```

Ответ `200 OK`:

```json
{
  "url": "https://practicum.yandex.ru"
}
```

При ошибках API возвращает `400` или `404` с телом вида
`{"message": "..."}`.

## Автор

Олег Роговенко — [GitHub](https://github.com/0legRogovenko)

### Установка

1. Скачать и установить [Python 3.11](https://www.python.org/downloads/)
2. Скачать и установить [Poetry](https://python-poetry.org/docs/#installation)
3. Скачать и установить [PostgreSQL](https://www.postgresql.org/download/)

### Запуск
1. Склонировать репозиторий
2. Переместиться в папку с проектом
3. Установить зависимости командой `poetry install`
4. Заполнить config.yaml
5. Запустить бота командой `poetry run python crying/main.py`

### Доп информация
1. Вход в консоль PostgreSQL: `sudo -u postgres psql`
2. Создание базы данных: `CREATE DATABASE crying;`
3. Изменения пароля PostgreSQL: `\password`
4. Выход из консоли PostgreSQL: `\q`
5. Перезапуск PostgreSQL: `sudo service postgresql restart`
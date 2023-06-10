# AiogramProjectTemplate

#### Шаблон бота на aiogram 3 с некоторым базовым функционалом.

####

- [Python 3.11](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [aiogram 3](https://github.com/aiogram/aiogram/tree/dev-3.x)
- [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy/)
- [PostgreSQL](https://www.postgresql.org/download/)

___

## Включает

- Админ панель
- Мидлвары
- Настройки локализации через Fluent
- Мерчанты
  - [CryptoCloud](https://cryptocloud.plus/)
  - [CryptoPay](https://github.com/LulzLoL231/pyCryptoPayAPI)
  - [Qiwi](https://qiwi.com/p2p-admin/api/)
  - [YooKassa](https://yookassa.ru/developers/)
  - USDT
  - ~~[Payeer](https://payeer.com/)~~
- CLI
- Настройка Вебхука
- Database ORM: [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy/)
- Удобная конфигурация проекта через [Pydantic](https://github.com/pydantic/pydantic)

## Создание проекта

Запустить скрипт `init_project.py`
Например `python3 init_project.py -p <your_project_dir> -d`

- `d` - установка зависимостей
- `p` - путь к папке проекта, default = `./`. Если папка не существует, то будет создан новый проект с
  помощью `poetry new <your_project_dir>`

## Локализация

Документация по [Fluent](https://projectfluent.org/fluent/guide/)
`project\crying\utils\ftl_parser_cli.py`
CLI для парсинга файлов переменных из ftl файлов в заглушку с поддержкой автодополнения,
используется [fluentogram](https://github.com/Arustinal/fluentogram)

По умолчанию папка локализации `crying\apps\bot\locales`.

## Дополнительно

Пример как использовать [тут](https://github.com/Arustinal/fluentogram/blob/main/example/TypingGenerator.md), вместо
i18n используется ftl_parser_cli
`ftl_parser_cli` дополнительно поддерживает

- `-dir-ftl` - для создания заглушки для указанной папки
- `-track-ftl` - для отслеживания изменений в файлах ftl в указанной папке и автоматического обновления заглушки

**Создание сертификата для webhook**

`openssl req -newkey rsa:2048 -sha256 -nodes -keyout private.key -x509 -days 3650 -out cert.pem`

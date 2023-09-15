# Aiogram Project Template

#### Этот шаблон был разработан для создания ботов на основе aiogram 3, и включает в себя несколько базовых функций.

#### Технологии

- [Python 3.11](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [aiogram 3](https://github.com/aiogram/aiogram/tree/dev-3.x)
- [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy/)
- [PostgreSQL](https://www.postgresql.org/download/)

___

## Возможности

- Административная панель
- Промежуточное программное обеспечение (Middleware)
- Настройка локализации через Fluent
- Поддержка платёжных систем:
  - [CryptoCloud](https://cryptocloud.plus/)
  - [CryptoPay](https://github.com/LulzLoL231/pyCryptoPayAPI)
  - [Qiwi](https://qiwi.com/p2p-admin/api/)
  - [YooKassa](https://yookassa.ru/developers/)
  - USDT
  - [Payeer](https://payeer.com/)
  - [Cryptomus](https://cryptomus.com/)
- Командная строка (CLI)
- Настройка Вебхука
- ORM базы данных: [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy/)
- Удобное управление конфигурацией проекта через [Pydantic](https://github.com/pydantic/pydantic)

## Инициализация проекта

Для инициализации проекта запустите скрипт `init_project.py`, пример: `python3 init_project.py -p <your_project_dir> -d`

- `-d` - установка зависимостей
- `-p` - путь к директории проекта, по умолчанию - `./`. Если указанная директория не существует, то будет создан новый
  проект с использованием `poetry new <your_project_dir>`

## Локализация

Для локализации используется [Fluent](https://projectfluent.org/fluent/guide/). Для парсинга переменных из файлов `.ftl`
в автозаполняемые заглушки используется утилита `project\crying\utils\ftl_parser_cli.py`, которая основана
на [fluentogram](https://github.com/Arustinal/fluentogram).

По умолчанию, папка с локализациями находится по пути `crying\locales`.

## Примечания

Пример использования доступен [здесь](https://github.com/Arustinal/fluentogram/blob/main/example/TypingGenerator.md).
Вместо `i18n` используется `ftl_parser_cli`. `ftl_parser_cli` поддерживает следующие дополнительные опции:

- `-dir-ftl` - создание заглушки для указанной директории
- `-track-ftl` - отслеживание изменений в файлах `.ftl` в указанной директории и автоматическое обновление заглушки

Для создания сертификата для вебхука используйте следующую команду:

`openssl req -newkey rsa:2048 -sha256 -nodes -keyout private.key -x509 -days 3650 -out cert.pem`
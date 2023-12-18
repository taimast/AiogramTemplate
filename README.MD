# Aiogram Project Template

#### Этот шаблон был разработан для создания ботов на основе aiogram 3, и включает в себя несколько базовых функций.


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
  - [WalletPay](https://pay.wallet.tg/)

- Командная строка (CLI)
- Настройка Вебхука
- ORM базы данных: [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy/)
- Инструмент миграции БД: [Alembic](https://github.com/sqlalchemy/alembic)
- Удобное управление конфигурацией проекта через [Pydantic](https://github.com/pydantic/pydantic)

## Инициализация проекта

Для инициализации проекта запустите скрипт `init_project.py`, пример: `python3 init_project.py -p <your_project_dir> -d`

- `-d` - установка зависимостей
- `-p` - путь к директории проекта, по умолчанию - `./`. Если указанная директория не существует, то будет создан новый
  проект с использованием `poetry new <your_project_dir>`

## Локализация

Для локализации используется [Fluent](https://projectfluent.org/fluent/guide/).  
По умолчанию, папка с локализациями находится по пути `crying/locales`.

## _Утилиты_
- `project/crying/utils/ftl_parser_cli.py` - Live генерация заглушек для локализации. 
- `project/crying/utils/ftl_translator.py` - Автоматический перевод локализации на все языки через Google Translate и генерация ftl.  
- `project/crying/apps/bot/callback_data/paginator.py` - Пагинатор страниц для InlineKeyboardMarkup. 
- `project/crying/db/models/user/mixins.py` - Миксины для моделей пользователей. На данный момент для Рефералки и Подключения пользователей к друг другу через бота. (Пример подключения в `helpers/connect`) 

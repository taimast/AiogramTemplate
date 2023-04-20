# AiogramProjectTemplate

#### Шаблон бота на aiogram 3 с некоторым базовым функционалом.

#### [Python 3.11](https://www.python.org/downloads/), [Poetry](https://python-poetry.org/docs/#installation), [aiogram 3](https://github.com/aiogram/aiogram/tree/dev-3.x), [PostgreSQL](https://www.postgresql.org/download/)

___

## Включает

- Админ панель
  - Статистика
  - Настройка обязательной подписки на каналы
  - Рассылка
  - Настройки бота
  - Экспорт пользователей
- Мидлвары
  - Проверка на подписку
  - Проверка на спам
  - Локализация Fluent
- Настройки локализации через Fluent
- Создание бекапа базы данных
- Мерчанты
  - [CryptoCloud](https://cryptocloud.plus/)
  - [Qiwi](https://qiwi.com/p2p-admin/api/)
  - [YooKassa](https://yookassa.ru/developers/)
  - ~~[Payeer](https://payeer.com/)~~
- CLI
- Логирование loguru
- Настройка Вебхука
- База данных [PostgreSQL](https://www.postgresql.org/download/
  ) + [Tortoise ORM](https://github.com/tortoise/tortoise-orm/) + [asyncpg](https://github.com/MagicStack/asyncpg)
- Удобная конфигурация проекта через [Pydantic](https://github.com/pydantic/pydantic)

## Создание проекта

Запустить скрипт `init_project.py`
Например `python3 init_project.py -p <your_project_dir> -d`

- `d` - установка зависимостей
- `p` - путь к папке проекта, default = `./`. Если папка не существует, то будет создан новый проект с
  помощью `poetry new <your_project_dir>`

**Создание сертификата для webhook**

`openssl req -newkey rsa:2048 -sha256 -nodes -keyout private.key -x509 -days 3650 -out cert.pem`

## Локализация

Локализация происходит с помощью [Fluent](https://projectfluent.org). По умолчанию папка
локализации `crying\apps\bot\locales`.

Для использования локализации необходимо создать файлы локализации расширением `.ftl`, в папке с кодом языка,
например `en` или `ru`

Документация по [Fluent](https://projectfluent.org/fluent/guide/)

## Дополнительно

`project\crying\utils\ftl_parser_cli.py`  
CLI для парсинга файлов переменных из ftl файлов в заглушку с поддержкой автодополнения,
используется [fluentogram](https://github.com/Arustinal/fluentogram)

Пример как использовать [тут](https://github.com/Arustinal/fluentogram/blob/main/example/TypingGenerator.md), вместо
i18n используется ftl_parser_cli  
`ftl_parser_cli` дополнительно поддерживает

- `-dir-ftl` - для создания заглушки для указанной папки
- `-track-ftl` - для отслеживания изменений в файлах ftl в указанной папке и автоматического обновления заглушки



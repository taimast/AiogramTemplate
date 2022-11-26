# AiogramProjectTemplateV4

Шаблон бота на aiogram 3 со всем необходимыми пакетами

## Включает
- Админ панели
  - Статистика 
  - Настройка обязательной подписки на каналы
  - Рассылка
  - Настройки бота
  - Экспорт пользователей
- Проверка на спам
- Настройки локализации через Fluent
- Создание бекапа базы данных
- Мерчанты
    - [CryptoCloud](https://cryptocloud.plus/)
    - [Qiwi](https://qiwi.com/p2p-admin/api/)
    - [YooKassa](https://yookassa.ru/developers/)
    - ~~[Payeer](https://payeer.com/)~~

## Создание проекта

Запустить скрипт `init_project.py`
Например `python3 init_project.py -p <your_project_dir> -d -l en`

- `d` - установка зависимостей, default = `True`
- `l` - язык локализации
- `p` - путь к папке проекта, default = `./`. Если папка не существует, то будет создан новый проект с
  помощью `poetry new <your_project_dir>`

# ceft create

`openssl req -newkey rsa:2048 -sha256 -nodes -keyout private.key -x509 -days 3650 -out cert.pem`

## Локализация

Локализация происходит с помощью [Fluent](https://projectfluent.org). По умолчанию папка
локализации `crying\apps\bot\locales`.

Для использования локализации необходимо создать файлы локализации расширением `.ftl`, в папке с названием языка,
например `en` или `ru`

Документация по [Fluent](https://projectfluent.org/fluent/guide/)

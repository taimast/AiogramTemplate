# Aiogram Project Template

#### This template was designed to create bots based on aiogram 3, and includes several basic functions.


## Features

- Administrative panel
- Middleware
- Localization settings via Fluent
- Support for payment systems:
  - [CryptoCloud](https://cryptocloud.plus/)
  - [CryptoPay](https://github.com/LulzLoL231/pyCryptoPayAPI)
  - [Qiwi](https://qiwi.com/p2p-admin/api/)
  - [YooKassa](https://yookassa.ru/developers/)
  - USDT
  - [Payeer](https://payeer.com/)
  - [Cryptomus](https://cryptomus.com/)
  - [WalletPay](https://pay.wallet.tg/)

- Command Line (CLI)
- Configuring the Webhook
- Database ORM: [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy /)
- DB Migration Tool: [Alembic](https://github.com/sqlalchemy/alembic )
- Convenient project configuration management via [Pydantic](https://github.com/pydantic/pydantic )

## Initialization of the project

To initialize the project, run the script `init_project.py `, example: `python3 init_project.py -p <your_project_dir> -d`

- `-d` - installing dependencies
- `-p` is the path to the project directory, by default - `./`. If the specified directory does not exist, a new one will be created
  a project using `poetry new <your_project_dir>`

## Localization

[Fluent] is used for localization(https://projectfluent.org/fluent/guide /).
By default, the folder with localizations is located at the path `crying/locales'.

## _utilities_
- `project/crying/utils/ftl_parser_cli.py ` - Live generation of stubs for localization.
- `project/crying/utils/ftl_translator.py ` - Automatic localization translation into all languages via Google Translate and ftl generation.
- `project/crying/apps/bot/callback_data/paginator.py ` - Paginator of pages for InlineKeyboardMarkup.
- `project/crying/db/models/user/mixins.py ` - Mixins for user models. At the moment, for Referrals and Connecting users to each other through a bot. (Example of connection in `helpers/connect')

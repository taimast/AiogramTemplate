# [Aiogram Project Template](https://github.com/taimast/AiogramTemplate)

#### This template was designed to create bots based on aiogram 3, and includes several basic functions.


## Features

- Admin panel
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
  - [Payok](https://payok.io/)
  - [Aaio](https://aaio.so/)
  - [BetaTransfer](https://betatransfer.io/)

- Command Line (CLI)
- Configuring the Webhook
- Database ORM: [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy)
- DB Migration Tool: [Alembic](https://github.com/sqlalchemy/alembic )
- Convenient project configuration management via [Pydantic](https://github.com/pydantic/pydantic )

## Localization

[Fluent](https://projectfluent.org/fluent/guide) is used for localization.
By default, the folder with localizations is located at the path `src/locales'.

## _utilities_
- `src/utils/ftl_parser_cli.py ` - Live generation of stubs for localization.
- `src/utils/ftl_translator.py ` - Automatic localization translation into all languages via Google Translate and ftl generation.
- `src/apps/bot/callback_data/paginator.py ` - Paginator of pages for InlineKeyboardMarkup.
- `src/db/models/user/mixins.py ` - Mixins for user models. At the moment, for Referrals and Connecting users to each other through a bot. (Example of connection in `helpers/connect')


### Installation

1. Fill in the `config.yml`
2. Run `docker compose up -d`

### When changing data

1. Run `docker compose stop` (stop container)
2. Run `docker compose up -d --build` (rebuild the container and run it)

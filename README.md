# [Aiogram Project Template](https://github.com/taimast/AiogramTemplate)

**A flexible template for creating bots using Aiogram 3, featuring powerful tools for admin management, payments, localization, and more.**

## ✨ Features

- **Admin Panel**: Comprehensive and easy-to-use admin interface.
- **Middleware**: Custom middlewares to handle user sessions, localization, and database interactions.
- **Localization**: Fluent localization system for multiple languages.
- **Payments**: Integrated support for multiple payment providers with [multi-merchant](https://github.com/taimast/multi-merchant).
- **Command Line Interface (CLI)**: Simplified management and configuration via command line.
- **Webhook Configuration**: Easy setup and management of webhooks for efficient bot operation.
- **Database ORM**: Fully integrated with [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) for database management.
- **DB Migration**: Database versioning with [Alembic](https://github.com/sqlalchemy/alembic).
- **Configuration Management**: Robust configuration handling using [Pydantic](https://github.com/pydantic/pydantic).
- **Persistence Sessions**: Efficient handling of user data across multiple persistence sessions.
- **Support Sessions**: Direct communication between users and support moderators through structured threads.

## 📦 Usage
**Configure the Project:**
- Fill in the `config.yml` with your specific settings.
**Run the Project:**
- Start the project using Docker: `docker compose up -d`.

#### Updating the Project
**Stop the Containers:**
- Run `docker compose stop` to stop the running containers.
**Rebuild and Restart:**
- Use `docker compose up -d --build` to rebuild and restart the containers.

## 🗂️ Project Structure

- **`src/apps`**: Contains bot-related logic, including handlers, middlewares, and localization.
- **`src/config`**: Configuration files and environment settings.
- **`src/db`**: Database models, migrations, and ORM settings.
- **`src/setup`**: Scripts for setting up the bot, including logging, scheduling, routers, and more.
- **`src/utils`**: Utility scripts for tasks like localization, callback generation, and more.

## 🌍 Localization

Localization is handled via [Fluent](https://projectfluent.org/fluent/guide). Default localization files are located in the `src/locales` directory.

## Utilities for Localization

- **Live Stub Generation**: `src/utils/ftl_parser_cli.py` – Automatically generates stubs for localization as you work.
- **Automatic Translation**: `src/utils/ftl_translator.py` – Translates localizations into multiple languages using Google Translate and generates corresponding FTL files.


## 🔧 Support Sessions
- **SupportSession Management**: `src/utils/support.py` – Facilitates direct communication between users and support moderators through structured threads.
  - **Seamless Support**: Manage user support requests effectively by utilizing the `SupportConnector`, which tracks and manages active support sessions.
  - **Session Handling**: Automatically create and manage communication threads for each support request, enabling efficient handling and resolution of user queries.
  - **Modular Integration**: Easily integrate into existing bots for enhanced user support capabilities.


## 💾 Persistence and Configuration
**Manager (`PersistenceSessionManager`)**: `src/db/persistence_session/manager.py`
   - Acts as a coordinator for handling both light and rich models across the different persistence sessions.
   - Initializes and synchronizes "light" user data (i.e., cached or minimal data structure) with "rich" data stored in the relational database.
   - Ensures that whenever a session is instantiated, it is ready to sync in-memory or Redis-stored data with the database.
   - Uses SQLAlchemy sessions for interacting with the database and potentially Redis for caching purposes.


## 🚀 Additional Functionalities

- **Callback Data Generator**: `src/utils/generate_callback.py` – Dynamically generates callback data classes for your bot.
- **Mailing System**: `src/utils/mailing.py` – Handles mass mailing and notifications to users with detailed progress tracking.
- **State Management**: `src/utils/state.py` – Simplified handling of user states within FSM context.
- **User Connection and Referral**: `src/db/models/user/mixins.py` – Mixins for managing user connections and referrals.

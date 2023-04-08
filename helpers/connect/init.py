import shutil
from pathlib import Path

CONNECT_SRC_DIR = Path(__file__).parent / "src"


def get_project_dir(project_path):
    for item in project_path.iterdir():
        if item.is_dir() and item.name not in ("tests",
                                               ".idea",
                                               "scripts",
                                               "logs",
                                               "media",
                                               "static",
                                               "templates",
                                               "venv",
                                               "__pycache__",
                                               "backup",
                                               ".git"):
            return item


def main():
    project_path = Path.cwd()
    workdir: Path = get_project_dir(project_path)
    confirm = input(f"Вы уверены, что хотите перезаписать файлы в {workdir}? [y/n]: ")
    if not confirm == "y":
        exit("Отмена")

    shutil.copyfile(CONNECT_SRC_DIR / "callback.py", workdir / "apps/bot/callback_data" / "connect.py")
    # C:/Users/taima/PycharmProjects/bots/order-channel-bot/order_channel_bot/apps/bot/handlers/common
    shutil.copyfile(CONNECT_SRC_DIR / "handler.py", workdir / "apps/bot/handlers/common" / "connect.py")
    # C:/Users/taima/PycharmProjects/bots/order-channel-bot/order_channel_bot/apps/bot/filters
    shutil.copyfile(CONNECT_SRC_DIR / "filter.py", workdir / "apps/bot/filters" / "connect.py")
    # C:/Users/taima/PycharmProjects/bots/order-channel-bot/order_channel_bot/apps/bot/keyboards/common
    shutil.copyfile(CONNECT_SRC_DIR / "kbs.py", workdir / "apps/bot/keyboards/common" / "connect_kbs.py")
    # C:/Users/taima/PycharmProjects/bots/order-channel-bot/order_channel_bot/db/models/user.py
    shutil.copyfile(CONNECT_SRC_DIR / "model.py", workdir / "db/models" / "user.py")
    # C:/Users/taima/PycharmProjects/bots/order-bot/order_bot/apps/bot/locales/ru/conversation.ftl
    shutil.copyfile(CONNECT_SRC_DIR / "conversation.ftl", workdir / "apps/bot/locales/ru" / "conversation.ftl")

    print("✅ Файлы скопированы")


if __name__ == '__main__':
    main()

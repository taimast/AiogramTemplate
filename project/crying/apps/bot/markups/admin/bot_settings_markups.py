from aiogram.utils.keyboard import InlineKeyboardBuilder


def bot_setting_start(bot_running: bool):
    keywords = [
        ("🚫 Приостановить", "stop_bot") if bot_running else ("▶ Запустить", "run_bot"),
        ("🔃 Перезапустить", 'restart_bot'),
        ("⬅️ Назад", "admin"),
    ]
    builder = InlineKeyboardBuilder()
    for keyword, payload in keywords:
        builder.button(text=keyword, callback_data=payload)

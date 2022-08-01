import re

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from project.crying.apps.bot.callback_data.base_callback import ChannelCallback, Action


# todo 5/31/2022 2:33 PM taima: разделить основно функционал
def admin_start():
    keywords = [
        ("📄 Список каналов для обязательной подписки", ChannelCallback(action=Action.all)),
        ("✍ Добавить канал для обязательной подписки", ChannelCallback(action=Action.create)),
        ("📈 Общая информация о боте", "statistics"),
        ("🔖 Сделать рассылку", "send_mail"),
        ("⚙ Настройки бота", "bot_settings"),
        ("👥 Экспорт пользователей", "export_users"),
        # ("✍ Изменить текст меню", "change_menu"),
    ]
    builder = InlineKeyboardBuilder()

    for text, callback_data in keywords:
        builder.button(text=text, callback_data=callback_data)

    builder.adjust(1)
    return builder.as_markup()
    # return get_inline_keyboard(keyword)


def admin_button() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Админ панель", callback_data="admin")
    return builder.as_markup()


def back() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data="admin")
    return builder.as_markup()


def export_users_send_type() -> InlineKeyboardMarkup:
    keywords = [
        ("Отправить сообщением", "text"),
        ("Отправить тестовый файл", "txt"),
        ("Отправить json-file", "json"),
    ]
    builder = InlineKeyboardBuilder()

    for text, callback_data in keywords:
        builder.button(text=text, callback_data=callback_data)

    builder.button(text="⬅️ Назад", callback_data="admin")
    builder.adjust(1)
    return builder.as_markup()


def send_mail_preview() -> InlineKeyboardMarkup:
    keywords = [
        ("➕ Добавить url кнопки", "add_button"),
        ("✅ Подтвердить", "accept"),
    ]
    builder = InlineKeyboardBuilder()
    for text, callback_data in keywords:
        builder.button(text=text, callback_data=callback_data)

    builder.button(text="❌ Отменить", callback_data="admin")
    builder.adjust(1)
    return builder.as_markup()


def send_mail_done(status: bool = True) -> InlineKeyboardMarkup:
    keywords = [
        ("⏸ Пауза", "pause_mail") if status else ("▶️ Возобновить", "continue_mail"),
        ("⏹ Стоп", "stop_mail")
    ]
    builder = InlineKeyboardBuilder()

    for text, callback_data in keywords:
        builder.button(text=text, callback_data=callback_data)

    return builder.as_markup()


def parse_buttons(text: str):
    keywords = []
    change_keyboard = re.split(r'(?<=\w\n)', text)
    for but_parent in change_keyboard:
        keywords.append(
            list(map(lambda x: list(map(lambda y: y.strip(), x.split('-'))), but_parent.split("|\n")))
        )
    return keywords


def send_mail_add_button(text: str) -> InlineKeyboardMarkup:
    keywords = [
        # ("➕ Добавить еще url кнопки", "add_button"),
        ("➕ Добавить новый url кнопки", "add_button"),
        ("✅ Подтвердить", "accept"),
        ("❌ Отменить", "cancel"),
    ]
    builder = InlineKeyboardBuilder()
    for _text, callback_data in keywords:
        builder.button(text=_text, callback_data=callback_data)

    parsed_buttons_group: list[list[list]] = parse_buttons(text)
    for buttons in parsed_buttons_group:
        for _text, callback_data in buttons:
            builder.button(text=_text, callback_data=callback_data)

    return builder.as_markup()


def send_mail_add_button_save_keyboard(text: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    parsed_buttons_group: list[list[list]] = parse_buttons(text)
    for buttons in parsed_buttons_group:
        for _text, callback_data in buttons:
            builder.button(text=_text, callback_data=callback_data)

    return builder.as_markup()


def send_mail_add_button_in_current(markup: InlineKeyboardMarkup) -> InlineKeyboardMarkup:
    keywords = [
        # ("➕ Добавить еще url кнопки", "add_button"),
        ("➕ Добавить новый url кнопки", "add_button"),
        ("✅ Подтвердить", "accept"),
        ("❌ Отменить", "cancel"),
    ]
    builder = InlineKeyboardBuilder()
    for _text, callback_data in keywords:
        builder.button(text=_text, callback_data=callback_data)

    new_markup = builder.as_markup()
    copy_markup = markup.copy()
    copy_markup.inline_keyboard.extend(new_markup.inline_keyboard)

    return copy_markup


if __name__ == '__main__':
    texts = ("Кнопка 1 - https://www.example1.com\n"
             "Кнопка 2 - https://www.example2.com\n"
             "Кнопка 3 - https://www.example3.com\n"
             "Кнопка 4 - https://www.example4.com")
    # pprint(send_mail_preview().inline_keyboard)
    print(*parse_buttons(texts))
    # print(parse_buttons(text))
    # print(send_mail_add_button(text))
    # parse_buttons("Кнопка 1 - https://www.example1.com,\n"
    #               "Кнопка 2 - https://www.example2.com,\n"
    #               "Кнопка 3 - https://www.example3.com|\n"
    #               "Кнопка 4 - https://www.example4.com\n")

from aiogram.types import (
    CopyTextButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

from src.apps.bot.callback_data.paginator import PaginatorCallback
from src.apps.bot.keyboards.common.helper_kbs import (
    CustomInlineKeyboardBuilder,
    CustomReplyKeyboardBuilder,
)
from src.db.models.user.locale import Locale


def start() -> ReplyKeyboardMarkup:
    builder = CustomReplyKeyboardBuilder()
    start_app_url = "https://t.me/WaterMarkTgBot?start=123456789"
    text = "Hello, World!"
    share_link_part = f"share/url?text={text}&url={start_app_url}"
    share_link = f"https://t.me/{share_link_part}"
    builder.button(
        text="share",
        # web_app=WebAppInfo(url=share_link)
    )
    builder.add_back()
    return builder.as_markup(resize_keyboard=True)


def inline_start() -> InlineKeyboardMarkup:
    builder = CustomInlineKeyboardBuilder()
    builder.button(text="start", url="https://t.me/")
    builder.button(
        text="webapp",
        web_app=WebAppInfo(url="https://preferably-fit-asp.ngrok-free.app"),
    )

    builder.button(text="Taimast", web_app=WebAppInfo(url="https://taimast.ru"))
    builder.button(text="payment", callback_data="payments")
    builder.button(text="payment2", callback_data="payments2")
    builder.button(
        text="Добавить бота в канал админом",
        url="https://t.me/WaterMarkTgBot?start=123456789",
    )
    #       const startAppUrl = `https://t.me/${botUsername}?start=${user.id}`
    #       const shareLinkPart = `share/url?text=${text}&url=${startAppUrl}`
    #       const shareLink = `https://t.me/${shareLinkPart}`
    start_app_url = "https://t.me/WaterMarkTgBot?start=123456789"
    text = "Hello, World!"
    share_link_part = f"share/url?text={text}&url={start_app_url}&button=share"
    share_link = f"https://t.me/{share_link_part}"
    builder.button(text="share", url=share_link)
    builder.button(text="give", copy_text=CopyTextButton(text="KO"))
    builder.adjust(1)
    # builder.add_start_back()
    return builder.as_markup(resize_keyboard=True)


def languages(l10n) -> ReplyKeyboardMarkup:
    builder = CustomReplyKeyboardBuilder()
    for locale in Locale:
        builder.button(text=l10n.get(f"language-button-{locale}.icon"))

    builder.adjust(1, 2)
    return builder.as_markup(resize_keyboard=True)


def test_paginator(
    data: list[str],
    pg: PaginatorCallback,
) -> InlineKeyboardMarkup:
    builder = CustomInlineKeyboardBuilder()
    # for i in pg.slice(data):
    #     builder.button(text=i)
    # builder.adjust(8)

    pg.add_minimal_pagination_buttons(builder, len(data))
    pg.add_sort_buttons(builder)
    return builder.as_markup()


def thread_support():
    builder = CustomReplyKeyboardBuilder()
    builder.button(text="[Disconned User]")
    builder.button(text="[Close Thread]")
    return builder.as_markup(
        is_persistent=True,
        selective=True,
        one_time_keyboard=True,
    )


def thread_support2():
    builder = CustomInlineKeyboardBuilder()
    builder.button(text="[Disconned User]", callback_data="disconnect_user")
    builder.button(text="[Close Thread]", callback_data="close_thread")
    return builder.as_markup(is_persistent=True)

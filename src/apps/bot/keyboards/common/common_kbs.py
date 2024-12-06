from aiogram.types import (
    CopyTextButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    WebAppInfo,
    KeyboardButtonRequestUsers,
)

from src.apps.bot.keyboards.common.helper_kbs import (
    CustomReplyKeyboardBuilder,
    CustomInlineKeyboardBuilder,
)


def start() -> ReplyKeyboardMarkup:
    builder = CustomReplyKeyboardBuilder()
    start_app_url = "https://t.me/WaterMarkTgBot?start=123456789"
    text = "Hello, World!"
    share_link_part = f"share/url?text={text}&url={start_app_url}"
    share_link = f"https://t.me/{share_link_part}"
    print(share_link)
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
    builder.button(text="give", copy_text={"text": "KJKJKJK"})
    builder.adjust(1)
    # builder.add_start_back()
    return builder.as_markup(resize_keyboard=True)

from aiogram.utils.keyboard import InlineKeyboardBuilder

from project.crying.apps.bot.callback_data.base_callback import ChannelCallback, Action
from project.crying.db.models import Channel


def view_channels(channels: list[Channel]):
    builder = InlineKeyboardBuilder()
    for c in channels:
        builder.button(
            text=str(c),
            callback_data=ChannelCallback(pk=c.pk, action=Action.view)
        )
    return builder.as_markup()


def touch_channel(channel):
    builder = InlineKeyboardBuilder()
    builder.button(text="✍ Удалить.", callback_data=ChannelCallback(pk=channel.pk, action=Action.delete))
    builder.button(text="⬅️ Назад", callback_data="admin")
    builder.adjust(1)
    return builder.as_markup()

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ...callback_data.dialog import PaginationCallback, PagiAction
from ...keyboards.common.common_kbs import inline_button


def pagination(
        item_list: list[str],
        offset: int = 0,
        page_size: int = 18,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in item_list[offset:offset + page_size]:
        # todo L1 TODO 06.04.2023 2:35 taima: Do something with this
        pass

    builder.adjust(2)
    back_button = False

    dialog_callback = PaginationCallback(
        action=PagiAction.prev,
        offset=offset,
    )
    if offset > 0:
        back_button = True
        dialog_callback.offset = offset - page_size
        builder.row(InlineKeyboardButton(text="≺ Prev",
                                         callback_data=dialog_callback.pack()))

    if offset + page_size < len(item_list):
        dialog_callback.offset = offset + page_size
        next_button = InlineKeyboardButton(text="≻ Next", callback_data=dialog_callback.pack())
        builder.add(next_button) if back_button else builder.row(next_button)
    # Ввести в ручную
    builder.button(inline_button("« Назад", "start"))
    return builder.as_markup()

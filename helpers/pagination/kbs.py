def products(
        products: list[str],
        l10n: TranslatorRunner,
        offset: int = 0,
        page_size: int = 18,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for product in products[offset:offset + page_size]:
        builder.button(
            text=product,
            callback_data=CategoryCallback(
                type=TypeEnum.PRODUCT,
                action=Action.GET,
                direction=product
            )
        )

    builder.adjust(2)
    back_button = False

    dialog_callback = PaginationCallback(
        action=DialogAction.prev,
        offset=offset,
    )
    if offset > 0:
        back_button = True
        dialog_callback.offset = offset - page_size
        builder.row(InlineKeyboardButton(text="≺ Prev",
                                         callback_data=dialog_callback.pack()))

    if offset + page_size < len(products):
        dialog_callback.offset = offset + page_size
        next_button = InlineKeyboardButton(text="≻ Next", callback_data=dialog_callback.pack())
        builder.add(next_button) if back_button else builder.row(next_button)

    builder.row(custom_back_button(l10n, CategoryCallback(type=TypeEnum.CATEGORY, action=Action.GET)))
    return builder.as_markup()

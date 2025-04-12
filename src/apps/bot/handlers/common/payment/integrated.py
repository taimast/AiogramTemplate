from pprint import pformat

from aiogram import F, Router, types
from loguru import logger

from src.apps.bot.types.message import NonEmptyMessageCallbackQuery

on = Router(name=__name__)

PAYMENT_PROVIDE_TOKEN = "3817642678:TEST:293290"


@on.callback_query(F.data == "payments")
async def process_callback_pay(call: NonEmptyMessageCallbackQuery):
    await call.message.answer("Платежная система")
    await call.message.answer_invoice(
        title="Оплата подписки",
        description="Оплата подписки на 1 месяц",
        # provider_token=PAYMENT_PROVIDE_TOKEN,
        provider_token="",
        # currency='rub',
        currency="XTR",
        prices=[
            types.LabeledPrice(label="1 месяц", amount=1),
            # types.LabeledPrice(label='Test2', amount=20000)
        ],
        start_parameter="test-invoice",
        is_flexible=False,
        payload="test-invoice",
    )


@on.callback_query(F.data == "payments-link")
async def process_callback_pay_link(call: NonEmptyMessageCallbackQuery):
    invoice = await call.bot.create_invoice_link(
        title="Оплата подписки",
        description="Оплата подписки на 1 месяц",
        # provider_token=PAYMENT_PROVIDE_TOKEN,
        provider_token="",
        # currency="rub",
        currency="XTR",
        prices=[
            types.LabeledPrice(label="1 месяц", amount=1),
            # types.LabeledPrice(label="Test2", amount=20000)
        ],
        is_flexible=False,
        payload="test-invoice",
        subscription_period=2592000,
        # max_tip_amount=100,
        # suggested_tip_amounts=[10, 20, 50, 100],
    )

    await call.message.answer(invoice)


@on.shipping_query()
async def process_shipping_query(shipping_query: types.ShippingQuery):
    logger.info("process_shipping_query")
    logger.info(pformat(shipping_query.model_dump()))
    await shipping_query.answer(
        ok=True,
        shipping_options=[
            types.ShippingOption(
                id="1",
                title="Test",
                prices=[types.LabeledPrice(label="Что такое", amount=10000)],
            ),
            types.ShippingOption(
                id="2",
                title="Test2",
                prices=[types.LabeledPrice(label="Что такое2", amount=20000)],
            ),
        ],
        error_message="Test error message",
    )


@on.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    logger.info("process_pre_checkout_query")
    logger.info(pformat(pre_checkout_query.model_dump()))
    await pre_checkout_query.answer(ok=True, error_message="Test error message")


@on.message(F.content_type == types.ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    logger.info("process_successful_payment")
    logger.info(pformat(message.model_dump()))
    await message.answer(
        "Спасибо за покупку! {}".format(message.successful_payment.total_amount)
    )

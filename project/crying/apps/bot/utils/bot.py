from pydantic import BaseModel

from project.crying.apps.bot.utils.send_mail import MailSender
from project.crying.db.models import Channel


class TempData(BaseModel):
    """Данные для временного хранения в памяти"""
    subscription_channels: list[Channel]
    """ Список каналов для подписки """
    mail_sender: MailSender | None
    """ Объект для отправки писем """
    bot_running: bool
    """ Флаг запуска бота """

    # _: typing.Callable[[...], str] |None
    # """ Объект для перевода """

    class Config:
        arbitrary_types_allowed = True
        copy_on_model_validation = False

import typing

from loguru import logger
from tortoise import fields, models

if typing.TYPE_CHECKING:
    from .user import User


class AbstractSubscription(models.Model):
    pass


# todo 5/31/2022 12:38 PM taima: сделать дневной лимит
class SubscriptionTemplate(models.Model):
    """Шаблоны для создания подписок"""

    title = fields.CharField(255, default="Базовая подписка", index=True)
    price = fields.IntField(default=0)
    duration = fields.IntField(default=1)

    def __str__(self):
        return self.title

    @property
    def view(self):
        return f"Название: {self.title}\n" f"Цена: {self.price}\n" f"Длительность подписки: {self.duration}\n"

    @classmethod
    async def create_from_dict(cls, data: list | dict) -> list | tuple["SubscriptionTemplate", bool]:
        if isinstance(data, list):
            return [await SubscriptionTemplate.get_or_create(**obj) for obj in data]
        else:
            return await SubscriptionTemplate.get_or_create(**data)

    @classmethod
    async def refresh_subscription_templates(cls, sub_data: list[dict]):
        await cls.create_from_dict(sub_data)
        logger.info("Subscriptions refreshed")

    @classmethod
    async def update_subscriptions(cls, sub_data: list[dict]):
        await SubscriptionTemplate.create_from_dict(sub_data)
        for sub in await SubscriptionTemplate.all():
            for d_sub in sub_data:
                if sub.title == d_sub["title"]:
                    break
            else:
                await sub.delete()
        logger.info("Subscriptions updated")


class Subscription(SubscriptionTemplate):
    """Подписки с привязкой к пользователю"""

    user: "User" = fields.OneToOneField(
        "models.User",
    )

    def is_active(self):
        return self.duration > 0

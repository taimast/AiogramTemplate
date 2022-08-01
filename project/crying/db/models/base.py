import datetime

from tortoise import fields, models

from project.crying.config import TIME_ZONE


class TimestampMixin:
    created_at = fields.DatetimeField(null=True, auto_now_add=True)
    modified_at = fields.DatetimeField(null=True, auto_now=True)


class Channel(TimestampMixin, models.Model):
    skin = fields.CharField(100, index=True)
    username = fields.CharField(100, index=True)

    def __str__(self):
        return f"{self.skin} [{self.username}]"

    @property
    def at_username(self):
        return self.username[1:]


class User(TimestampMixin, models.Model):
    id = fields.BigIntField(pk=True)
    username = fields.CharField(32, unique=True, index=True, null=True)
    first_name = fields.CharField(255, null=True)
    last_name = fields.CharField(255, null=True)
    locale = fields.CharField(32, default="ru")
    is_search = fields.BooleanField(default=False)

    @classmethod
    async def count_all(cls) -> int:
        return await cls.all().count()

    @classmethod
    async def count_new_today(cls) -> int:
        date = datetime.datetime.now(TIME_ZONE)
        return await User.filter(
            registered_at__year=date.year,
            registered_at__month=date.month,
            registered_at__day=date.day,
        ).count()

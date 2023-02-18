from tortoise import Model as _Model, fields


class Model(_Model):

    async def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        await self.save(update_fields=kwargs.keys())


class ChannelForSubscription(Model):
    id = fields.BigIntField(pk=True)
    chat_id = fields.CharField(100, index=True)  # chat id or chat username with "@"
    skin = fields.CharField(100)  # skin for view

    def __str__(self) -> str:
        return f"{self.chat_id} [{self.skin}]"


class AbstractUser(Model):
    id = fields.BigIntField(pk=True)
    username = fields.CharField(32, index=True, null=True)
    first_name = fields.CharField(255, null=True)
    last_name = fields.CharField(255, null=True)
    is_bot = fields.BooleanField(default=False, null=True)
    is_premium = fields.BooleanField(null=True)
    registered_at = fields.DatetimeField(null=True, auto_now_add=True)
    updated_at = fields.DatetimeField(null=True, auto_now=True)

    class Meta:
        abstract = True


class TimestampMixin:
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

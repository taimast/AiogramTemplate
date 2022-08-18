from tortoise import Model, fields


class Channel(Model):
    skin = fields.CharField(100, index=True)
    username = fields.CharField(100, index=True)

    def __str__(self):
        return f"{self.skin} [{self.username}]"

    @property
    def at_username(self):
        return self.username[1:]


class TimestampMixin:
    created_at = fields.DatetimeField(null=True, auto_now_add=True)
    modified_at = fields.DatetimeField(null=True, auto_now=True)


class AbstractUser(Model):
    id = fields.BigIntField(pk=True)
    username = fields.CharField(32, unique=True, index=True, null=True)
    first_name = fields.CharField(255, null=True)
    last_name = fields.CharField(255, null=True)
    registered_at = fields.DatetimeField(null=True, auto_now_add=True)

    class Meta:
        abstract = True

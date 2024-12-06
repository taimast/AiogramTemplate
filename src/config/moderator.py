from pydantic import BaseModel

from src.apps.bot.callback_data.moderator import ModeratorPermission
from src.db.models import Locale


class Moderator(BaseModel):
    id: int
    username: str | None = None
    permissions: list[ModeratorPermission] = []
    locale: Locale | None = None

    def have_permission(self, permission: ModeratorPermission) -> bool:
        return permission in self.permissions

    def switch_permission(self, permission: ModeratorPermission):
        if permission == ModeratorPermission.LOCALE:
            self.switch_locale()
        elif permission in self.permissions:
            self.permissions.remove(permission)
        else:
            self.permissions.append(permission)

    def switch_locale(self):
        if self.locale is None:
            self.locale = Locale.ENGLISH
        elif self.locale == Locale.ENGLISH:
            self.locale = Locale.RUSSIAN
        else:
            self.locale = None

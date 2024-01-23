from aiogram import F

from .actions import Action, ConnectAction
from .mixins import ActionMixin


class ConnectCallback(ActionMixin, prefix="connect"):
    action: Action | ConnectAction
    force: bool = False
    user_id: int | None = None
    service_id: int | None = None

    @classmethod
    def connect(cls):
        return cls(action=ConnectAction.CONNECT)

    @classmethod
    def filter_connect(cls):
        return cls.filter(F.action == ConnectAction.CONNECT)

    @classmethod
    def disconnect(cls):
        return cls(action=ConnectAction.DISCONNECT)

    @classmethod
    def filter_disconnect(cls):
        return cls.filter(F.action == ConnectAction.DISCONNECT)

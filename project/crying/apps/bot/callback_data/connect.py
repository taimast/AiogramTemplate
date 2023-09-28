from enum import StrEnum

from aiogram.filters.callback_data import CallbackData


class ConnectAction(StrEnum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"


class ConnectCallback(CallbackData, prefix="connect"):
    action: ConnectAction
    force: bool = False
    user_id: int | None = None
    service_id: int | None = None

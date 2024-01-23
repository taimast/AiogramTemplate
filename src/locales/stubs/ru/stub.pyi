from typing import Literal


class TranslatorRunner:
    def get(self, path: str, **kwargs) -> str: ...

    button: Button
    channel: Channel

    @staticmethod
    def start(*, name) -> Literal["""Привет { $name }. Я бот."""]: ...


class Button:
    @staticmethod
    def back() -> Literal["""«"""]: ...


class Channel:
    button: ChannelButton

    @staticmethod
    def subscribe() -> Literal["""🔻 Для продолжения нужно подписаться на каналы"""]: ...


class ChannelButton:
    @staticmethod
    def subscribe() -> Literal["""≻ Подписаться"""]: ...

    @staticmethod
    def subscribed() -> Literal["""✔️ Я подписался"""]: ...

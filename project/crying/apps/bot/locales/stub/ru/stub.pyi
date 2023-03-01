from typing import Literal


class TranslatorRunner:
    def get(self, path: str, **kwargs) -> str: ...

    @staticmethod
    def start(*, name) -> Literal["""Привет { $name }. Я бот."""]: ...

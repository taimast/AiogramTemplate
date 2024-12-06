from __future__ import annotations

from enum import StrEnum

from fluentogram import TranslatorRunner

flag_emojis = {
    "en": "🇬🇧",
    "ru": "🇷🇺",
    "ar": "🇸🇦",
    "zh": "🇨🇳",
    "es": "🇪🇸",
    "fr": "🇫🇷",
    "de": "🇩🇪",
    "hi": "🇮🇳",
    "ja": "🇯🇵",
    "pt": "🇵🇹",
    "tr": "🇹🇷",
    "uk": "🇺🇦",
    # Филипппины тагальский язык но с кодом страны
    "ph": "🇵🇭",
    # Филлипины тагальский язык
    "tl": "🇵🇭",
    # Индонезия
    "id": "🇮🇩",
    "ko": "🇰🇷",
}
reverse_flag_emojis = {v: k for k, v in flag_emojis.items()}


class Locale(StrEnum):
    """Language codes."""

    ENGLISH = "en"
    RUSSIAN = "ru"

    ARAB = "ar"
    CHINESE = "zh"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    INDIAN = "hi"
    JAPANESE = "ja"
    PORTUGUESE = "pt"
    TURKISH = "tr"
    UKRAINIAN = "uk"

    PHILIPPINE = "tl"
    INDONESIAN = "id"
    # Корейский
    KOREAN = "ko"

    @classmethod
    def get_locale_by_flag(cls, flag: str) -> Locale:
        return cls(reverse_flag_emojis[flag])

    def get_text(self, l10n: TranslatorRunner) -> str:
        return l10n.get(f"language-button-{self}")

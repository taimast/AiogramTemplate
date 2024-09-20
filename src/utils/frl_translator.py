import asyncio
from pathlib import Path

from ftl_translator import Locale as TranslateLocale, TranslateOpts, translate

BASE_DIR = Path(__file__).parent.parent
LOCALES_DIR = BASE_DIR / "locales"


async def main():
    origin_locale = "ru"
    origin_locale_dir = Path(LOCALES_DIR, origin_locale)
    # Хинди, немецкий, француский, испанский, etc.
    # target_locales = ["en", "hi", "de", "fr", "es", "it", "ja", "ko", "pt"]
    target_locales = [
        "en",
        # "ar",
        # "zh-CN",
        # "es",
        # "fr",
        # "de",
        # "hi",
        # "ja",
        # "pt",
        # "tr",
        # "uk",
    ]
    only_files = ["admin.ftl"]
    opts = TranslateOpts(
        locales_dir=LOCALES_DIR,
        origin_locale=TranslateLocale(origin_locale),
        target_locales=[TranslateLocale(locale) for locale in target_locales],
    )
    print(opts)
    # return
    await translate(opts)


if __name__ == "__main__":
    asyncio.run(main())

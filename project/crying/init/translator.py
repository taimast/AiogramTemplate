from fluent_compiler.bundle import FluentBundle
from fluentogram import TranslatorHub, FluentTranslator
from loguru import logger

from ..config import LOCALES_DIR
from ..db.models.user import Locale


# todo L1  01.03.2023 15:15 taima: Перенести в config
def init_translator_hub() -> TranslatorHub:
    """
    Initialize localization.
    Get all locales from LOCALES_DIR and create TranslatorHub.
    :return:
    """

    locales_map = {
        locale: (locale, "en")
        for locale in Locale
    }
    translators = [
        FluentTranslator(
            locale,
            translator=FluentBundle.from_files(locale, filenames=LOCALES_DIR.glob(f"{locale}/*.ftl"))
        )
        for locale in Locale
    ]

    translator_hub = TranslatorHub(
        locales_map=locales_map,
        translators=translators,
    )
    logger.info(f"Successfully loaded locales : " + ", ".join(translator_hub.locales_map))
    return translator_hub

from pathlib import Path

from fluent_compiler.bundle import FluentBundle
from fluentogram import TranslatorHub, FluentTranslator
from loguru import logger

from ..config import LOCALES_DIR
from ..db.models.user import Locale


def get_ftl_paths(path: Path) -> list[Path]:
    paths = []
    if not path.exists():
        return paths
    for file in path.iterdir():
        if file.is_dir():
            paths.extend(get_ftl_paths(file))
        elif file.suffix == ".ftl":
            paths.append(file)
    return paths


# todo L1  01.03.2023 15:15 taima: Перенести в config
def init_translator_hub() -> TranslatorHub:
    """
    Initialize localization.
    Get all locales from LOCALES_DIR and create TranslatorHub.
    :return:
    """

    locales_map = {
        locale: (locale, "ru", "en")
        for locale in Locale
    }

    translators = [
        FluentTranslator(
            locale,
            translator=FluentBundle.from_files(
                locale,
                filenames=get_ftl_paths(LOCALES_DIR / locale))
        )
        for locale in Locale
    ]

    translator_hub = TranslatorHub(
        locales_map=locales_map,
        translators=translators,
    )
    logger.info("Successfully loaded locales : " + ", ".join(translator_hub.locales_map))
    return translator_hub

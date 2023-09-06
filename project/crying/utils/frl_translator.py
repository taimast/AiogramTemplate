import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import deep_translator
from fluent.syntax import FluentParser, FluentSerializer, ast
from loguru import logger

BASE_DIR = Path(__file__).parent.parent
LOCALES_DIR = BASE_DIR / "locales"


class Serializer(FluentSerializer):
    def serialize(self, resource: ast.Resource) -> list[str]:
        "Serialize a :class:`.ast.Resource` to a string."
        if not isinstance(resource, ast.Resource):
            raise Exception('Unknown resource type: {}'.format(type(resource)))

        state = 0

        parts: list[str] = []
        for entry in resource.body:
            if not isinstance(entry, ast.Junk) or self.with_junk:
                parts.append(self.serialize_entry(entry, state))
                if not state & self.HAS_ENTRIES:
                    state |= self.HAS_ENTRIES

        return parts


def prepare_chunk(
        chunk: str,
        gt: deep_translator.GoogleTranslator,
        origin_locale: str,
        target_locale: str,
        only_variables: list[str] = None,

) -> str | None:
    gt = deep_translator.GoogleTranslator(
        source=origin_locale,
        target=target_locale,
        # proxies={

        # }
    )
    strip_chunk = chunk.strip()
    if strip_chunk.startswith("#"):
        strip_chunk = re.sub(r"#.*", "", strip_chunk)
    strip_chunk = strip_chunk.strip()
    if not strip_chunk:
        return None

    variable = re.search(r"(\w+.*=).*", strip_chunk).group(1)

    if only_variables and variable not in only_variables:
        logger.info(f"[{origin_locale} -> {target_locale}] Skipping {variable}")
        return None

    if variable.startswith("locale-button"):
        return strip_chunk

    if "uni-" in variable:
        return strip_chunk

    text = strip_chunk.replace(variable, "")

    # replace numbers to include variables
    include_variables = re.findall(r"\{\s?\$\s?(\w+)\s?\}", text)
    for i, var in enumerate(include_variables):
        text = re.sub(r"\{\s?\$\s?" + var + r"\s?\}", "{ $" + str(i) + " }", text)

    # replace <code> and </code> to <c> and </c>
    text = text.replace("<code>", "<c>")
    text = text.replace("</code>", "</c>")

    print("PRE_TEXT", variable, text)
    translated_text = gt.translate(text)
    print("POST_TEXT", variable, translated_text)
    # replace back numbers to include variables
    for i, var in enumerate(include_variables):
        if target_locale == "de":
            translated_text = re.sub(r"\{\s?\$" + str(i) + r"\s?\}?", "{ $" + var + " }", translated_text)
        else:
            translated_text = re.sub(r"\{\s?\$" + str(i) + r"\s?\}", "{ $" + var + " }", translated_text)

    # replace <c> and </c> to <code> and </code>
    translated_text = translated_text.replace("<c>", "<code>")
    translated_text = translated_text.replace("</c>", "</code>")
    translated_text = translated_text.replace("</ c>", "</code>")

    if target_locale == "hi":
        translated_text = translated_text.replace("</ सी>", "</code>")

    if "button-back" in variable:
        translated_text = translated_text.replace('"', "«")

    # models name
    if "-text2" in variable and "-model-" in variable:
        # replace text in code tags in translated text to text in old text in code tags
        old_text_in_code_tags = re.search(r"<c>(.*)</c>", text).group(1)
        translated_text = re.sub(r"<code>.*</code>", f"<code>{old_text_in_code_tags}</code>", translated_text)

    if translated_text.startswith('[') or variable in ("dialog-message_removed =",):
        return f"{variable} {translated_text}"
    else:
        return f"{variable}\n    {translated_text}"


def get_changed_files(origin_locale_dir):
    only_files = []
    result = subprocess.run(f"git diff --name-only {origin_locale_dir}", shell=True, capture_output=True)
    for filepath in result.stdout.decode("utf-8").split("\n"):
        if filepath:
            only_files.append(filepath.split("/")[-1])
    return only_files


def main():
    origin_locale = "ru"
    origin_locale_dir = Path(LOCALES_DIR, origin_locale)
    # Хинди, немецкий, француский, испанский, etc.
    target_locales = ["en", "hi", "de", "fr", "es", "it", "ja", "ko", "pt"]
    # target_locales = ["de"]
    # only_files = ["common.ftl", "payment.ftl"]
    # Проверить измененные файлы в git
    # only_files = ["common.ftl", "payment.ftl", "admin.ftl", "user.ftl", "post.ftl", "channel.ftl", "channel_post.ftl"]
    only_files = get_changed_files(origin_locale_dir)
    only_variables = []
    for target_locale in target_locales:
        google_translator = deep_translator.GoogleTranslator(
            source=origin_locale,
            target=target_locale,
            # proxies={

            # }
        )

        logger.info(f"[{origin_locale} -> {target_locale}] Translating...")
        target_locale_dir = Path(LOCALES_DIR, target_locale)
        if not target_locale_dir.exists():
            target_locale_dir.mkdir()
        for file in origin_locale_dir.iterdir():
            if file.is_file():
                if only_files and file.name not in only_files:
                    continue

                with open(file, "r", encoding="utf-8") as f:
                    text = f.read()

                parser = FluentParser(with_spans=False)
                serializer = Serializer()
                resource = parser.parse(text)
                results = serializer.serialize(resource)

                with ThreadPoolExecutor(max_workers=15) as executor:
                    translated_chunks = executor.map(
                        lambda chunk: prepare_chunk(
                            chunk,
                            google_translator,
                            origin_locale,
                            target_locale,
                            only_variables
                        ),
                        results
                    )
                translated_chunks = filter(lambda x: x is not None, translated_chunks)
                translated_text = "\n\n".join(translated_chunks)

                with open(Path(target_locale_dir, file.name), "w", encoding="utf-8") as f:
                    f.write(translated_text)
                    # return
                logger.info(f"[{origin_locale} -> {target_locale}] Translated {file.name}")


if __name__ == '__main__':
    main()

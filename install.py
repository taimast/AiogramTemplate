import argparse
import os
import shutil
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent / "project"


def parse_args():
    parser = argparse.ArgumentParser(description="config_file")
    parser.add_argument("-d", "--dependencies", type=bool)
    parser.add_argument("-l", "--localization", type=str)
    args = parser.parse_args()
    return args.dependencies, args.localization


def read_file(file: Path):
    with open(file, "r", encoding="utf8") as f:
        return f.read()


def write_file(file, data):
    with open(file, "w", encoding="utf8") as f:
        return f.write(data)


def get_project_dir(project_path):
    for item in project_path.iterdir():
        if item.is_dir() and item.name not in ("tests", ".idea", "logs", "media"):
            return item


def create_setting_files(project_path: Path, project_name: str):
    for file in (".gitignore", "config.yaml", "config_dev.yaml"):
        shutil.copy(TEMPLATE_DIR / file, project_path / file)
        data = read_file(project_path / file).replace("crying", project_name)
        write_file(project_path / file, data)


def set_project_name_in_files(workdir: Path, project_name: str):
    for elem in workdir.iterdir():
        print(elem)
        if elem.is_dir():
            set_project_name_in_files(elem, project_name)
        else:
            if elem.suffix not in (".pyc", ".gitignore", ".idea"):
                data = read_file(elem).replace("crying", project_name)
                write_file(elem, data)


def install_dependencies():
    aiogram_version = '"aiogram=^3.0.0b3" -E i18n --allow-prereleases'
    dependencies = "loguru pydantic tortoise-orm[asyncpg] pyyaml APScheduler"
    os.system(f"poetry add {aiogram_version}")
    os.system(f"poetry add {dependencies}")


def init_localize(project_name: str, localization: str = "en"):
    os.system(f"pybabel extract ./{project_name}/ -o ./{project_name}/apps/bot/locales/{project_name}.pot")
    os.system(
        f"pybabel init -i ./{project_name}/apps/bot/locales/{project_name}.pot "
        f"-d ./{project_name}/apps/bot/locales/ -D {project_name} -l {localization}")


def main():
    dependencies, localization = parse_args()
    base_dir = Path(__file__).parent
    project_dir = base_dir / "project"
    project_dir.rename(base_dir.name)
    print(f"Настройка проекта {project_dir.name}.")
    set_project_name_in_files(project_dir, project_dir.name)
    print("Шаблон настроен")

    print("Установка зависимостей")
    if dependencies:
        os.system(f"poetry install")
        print("Зависимости установлены")
    if localization:
        init_localize(project_dir.name, localization)
        print("Локализация установлена")


if __name__ == "__main__":
    main()

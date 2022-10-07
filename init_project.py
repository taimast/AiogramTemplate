import argparse
import os
import shutil
from distutils import dir_util
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent / "project"


def parse_args():
    parser = argparse.ArgumentParser(description="config_file")
    parser.add_argument("-p", "--project-dir", type=str)
    parser.add_argument("-d", "--dependencies", type=bool)
    parser.add_argument("-l", "--localization", type=str)
    args = parser.parse_args()
    if args.project_dir:
        project_dir = Path(args.project_dir)
    else:
        project_dir = Path.cwd()
    return project_dir, args.dependencies, args.localization


def read_file(file: Path):
    with open(file, "r", encoding="utf-8") as f:
        return f.read()


def write_file(file, data):
    with open(file, "w", encoding="utf-8") as f:
        return f.write(data)


def get_project_dir(project_path):
    for item in project_path.iterdir():
        if item.is_dir() and item.name not in ("tests",
                                               ".idea",
                                               "logs",
                                               "media",
                                               "static",
                                               "templates",
                                               "venv",
                                               "__pycache__",
                                               "backup"):
            return item


def create_setting_files(project_path: Path, project_name: str):
    for file in (".gitignore", "config.yaml", "config_dev.yaml"):
        shutil.copy(TEMPLATE_DIR / file, project_path / file)
        data = read_file(project_path / file).replace("crying", project_name)
        write_file(project_path / file, data)


def set_project_name_in_files(workdir: Path, project_name: str):
    for elem in workdir.iterdir():
        if elem.is_dir():
            if elem.name not in ("__pycache__",):
                set_project_name_in_files(elem, project_name)
            else:
                print(f"❌ {elem}")
        else:
            if elem.suffix != ".pyc":
                data = read_file(elem)
                if elem.name == 'config.py':
                    data = data.replace("project/crying", project_name) \
                        .replace('project.crying', project_name) \
                        .replace('crying', project_name)
                else:
                    data = data.replace("project.crying", project_name)
                print(f"✅ {elem}")
                write_file(elem, data)
            else:
                print(f"❌ {elem}")


def install_dependencies():
    aiogram_version = '"aiogram=^3.0.0b5" -E i18n --allow-prereleases'
    dependencies = "loguru pydantic tortoise-orm[asyncpg] pyyaml APScheduler cachetools"
    os.system(f"poetry add {aiogram_version}")
    os.system(f"poetry add {dependencies}")


def init_localize(project_name: str, localization: str):
    os.system(f"pybabel extract ./{project_name}/ -o ./{project_name}/apps/bot/locales/{project_name}.pot")
    os.system(
        f"pybabel init -i ./{project_name}/apps/bot/locales/{project_name}.pot "
        f"-d ./{project_name}/apps/bot/locales/ -D {project_name} -l {localization}")


def main():
    # subprocess.Popen(['poetry', 'show', '--tree'])
    project_path, dependencies, localization = parse_args()
    print(f"Настройка проекта {project_path}.")

    workdir: Path = get_project_dir(project_path)
    project_name = workdir.name
    print(workdir)
    create_setting_files(project_path, project_name)
    print("Файлы настроек созданы")

    dir_util.copy_tree(str(TEMPLATE_DIR / "crying"), str(workdir))
    set_project_name_in_files(workdir, project_name)
    print("Шаблон настроен")

    if dependencies:
        print(f"Установка базовых зависимостей...")
        install_dependencies()

    if localization:
        init_localize(workdir.name, localization)


if __name__ == "__main__":
    main()

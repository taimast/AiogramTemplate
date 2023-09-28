import argparse
import os
import re
import shutil
import subprocess
from distutils import dir_util
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent / "project"


def parse_args():
    parser = argparse.ArgumentParser(description="config_file")
    parser.add_argument("-p", "--project", type=str)
    parser.add_argument("-d", "--dependencies", action="store_true", default=False)
    parser.add_argument("-im", "--ignore-merchant", action="store_true", default=False)
    args = parser.parse_args()
    return args.project, args.dependencies, args.ignore_merchant


def get_project_dir(project_path):
    for item in project_path.iterdir():
        if item.is_dir():
            if project_path.name.lower().replace("-", "_") in item.name.lower().replace("-", "_"):
                return item


def create_setting_files(project_path: Path, project_name: str):
    for file in (
            ".gitignore",
            "config.yml",
            "config_dev.yml",
            "README.md",
            "Dockerfile",
            "docker-compose.yml",
    ):
        if (TEMPLATE_DIR / file).exists():
            shutil.copy(TEMPLATE_DIR / file, project_path / file)
            file_path = project_path / file
            data = file_path.read_text(encoding="utf-8").replace("crying", project_name)
            file_path.write_text(data, encoding="utf-8")


def set_project_name_in_files(workdir: Path, project_name: str, ignore_merchant: bool = False):
    for elem in workdir.iterdir():
        if elem.is_dir():
            if ignore_merchant:
                if elem.name in ("merchant", "invoice"):
                    shutil.rmtree(elem)
                    print(f"❌ {elem} (ignore merchant)")
                    continue

            if elem.name not in ("__pycache__",):
                set_project_name_in_files(elem, project_name, ignore_merchant)
            else:
                print(f"❌ {elem}")
        else:
            if (elem.suffix != ".pyc") and ("dev" not in elem.name) and ("probe" not in elem.name):
                data = elem.read_text(encoding="utf-8")
                data = data.replace("project/crying", project_name) \
                    .replace('project.crying', project_name) \
                    .replace('crying', project_name)
                print(f"✅ {elem}")

                if ignore_merchant:
                    data = clear_module_imports(data)
                    if elem.name == "settings.py":
                        data = clear_annotated(data)

                elem.write_text(data, encoding="utf-8")
            else:
                print(f"❌ {elem}")


def clear_module_imports(data: str, keys: list[str] = ["merchant", "invoice"]):
    for key in keys:
        pattern = rf'^\s*from[^\n]*\.?{key}[^\n]*import[^\n]*\(([^\n]*\n)*?\)[^\n]*\n|^\s*from[^\n]*\.?{key}[^\n]*import[^\n]*\n'
        data = re.sub(pattern, '', data, flags=re.MULTILINE)
    return data


def clear_annotated(data: str):
    old = "merchants: list[MerchantAnnotated] = Field(default_factory=list)"
    return data.replace(old, "")


def install_dependencies(project_path: Path):
    aiogram_version = 'aiogram@latest --allow-prereleases -E fast'
    dependencies = ["loguru",
                    "pyyaml",
                    "APScheduler",
                    "cachetools",
                    # "glQiwiApi",
                    # "pycryptopay-sdk",
                    "apscheduler",
                    "fluentogram",
                    "watchdog",
                    "jinja2",
                    "sqlalchemy",

                    "asyncpg",
                    "aiosqlite",
                    "pydantic_settings",
                    "pydantic",
                    ]
    utils = ["watchdog", "sqlalchemy-utils", "psycopg2"]
    utils = " ".join(utils)
    dependencies = " ".join(dependencies)
    os.system(f"cd {project_path} && "
              f"poetry add {aiogram_version} && "
              f"poetry add {dependencies} &&"
              f"poetry add {utils} --group dev"
              )


def main():
    # subprocess.Popen(['poetry', 'show', '--tree'])
    project_path, dependencies, ignore_merchant = parse_args()
    if not project_path:
        _project_path = Path.cwd()
        permission = input(f"Путь до проекта не указан, установить в текущую директорию {_project_path}? [y/n]: ")
        if permission == "y":
            project_path = _project_path
        else:
            exit("Укажите путь до проекта через аргумент -p")

    project_path = Path(project_path)
    if not project_path.exists():
        permission = input(f"Директория {project_path} не существует, создать как новый проект? [y/n]: ")
        if permission == "y":
            subprocess.Popen(['poetry', 'new', str(project_path)]).wait()
            print("✅ Проект создан")
        else:
            exit("❌ Проект не создан. Укажите путь до проекта через аргумент -p")

    print(f"Настройка проекта {project_path}. Ignore Merchant: {ignore_merchant}")
    workdir: Path = get_project_dir(project_path)
    project_name = workdir.name
    print(workdir)
    create_setting_files(project_path, project_name)
    print("Файлы настроек созданы")

    dir_util.copy_tree(str(TEMPLATE_DIR / "crying"), str(workdir))
    # dir_util.copy_tree(str(TEMPLATE_DIR / "scripts"), str(project_path / "scripts"))
    dir_util.copy_tree(str(TEMPLATE_DIR / ".github"), str(project_path / ".github"))

    set_project_name_in_files(workdir, project_name, ignore_merchant)
    # set_project_name_in_files(project_path / "scripts", project_name)
    set_project_name_in_files(project_path / ".github", project_path.name)

    print("Шаблон настроен")

    if dependencies:
        print("Установка базовых зависимостей...")
        install_dependencies(project_path)


if __name__ == "__main__":
    main()

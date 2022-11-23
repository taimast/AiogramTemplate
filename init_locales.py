import argparse
import os
from pathlib import Path


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
                                               "backup",
                                               ".git"):
            return item


def _extract(project_name: str):
    os.system(f"pybabel extract ./{project_name}/ -o ./{project_name}/apps/bot/locales/{project_name}.pot")
    print(f"✅ Success extracted")

def init_localize(project_name: str, localization: str):
    _extract(project_name)
    os.system(
        f"pybabel init -i ./{project_name}/apps/bot/locales/{project_name}.pot "
        f"-d ./{project_name}/apps/bot/locales/ -D {project_name} -l {localization}")
    print(f"✅ Success initialized")


def update_localize(project_name: str):
    _extract(project_name)
    os.system(
        f"pybabel update -d ./{project_name}/apps/bot/locales -D {project_name} -i ./{project_name}/apps/bot/locales/{project_name}.pot")
    os.system(
        f"pybabel compile -d ./{project_name}/apps/bot/locales/ -D {project_name}"
    )
    print(f"✅ Success updated")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--update", action="store_true", default=False)
    parser.add_argument("-e", "--extract", action="store_true", default=False)
    parser.add_argument("-i", "--init", default=False)
    args = parser.parse_args()
    workdir: Path = get_project_dir(Path.cwd())
    if args.init:
        init_localize(workdir.name, args.init)
    elif args.extract:
        _extract(workdir.name)
    else:
        update_localize(workdir.name)


if __name__ == '__main__':
    main()

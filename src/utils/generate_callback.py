import inspect
import sys
from dataclasses import dataclass

from src.apps.bot.callback_data.actions import *
from src.config import BASE_DIR

imports = """
from aiogram import F
from aiogram.filters.callback_data import CallbackData
from enum import StrEnum
from .mixins import ActionMixin
from .actions import Action
"""


@dataclass
class GenCode:
    name: str
    code: str


def generate_class_code(*action_enums: type[StrEnum], gen_action: bool = False):
    template = f"""
{imports}"""

    for enum in action_enums:
        base_class_name = enum.__name__
        template += f"""from .actions import {base_class_name}"""
    template += "\n\n\n"

    for enum in action_enums:
        base_class_name = enum.__name__
        methods = []
        for action in enum:
            method = f"""
    @classmethod
    def {action.value}(cls):
        return cls(action={base_class_name}.{action.name})

    @classmethod
    def filter_{action.value}(cls):
        return cls.filter(F.action == {base_class_name}.{action.name})
"""
            methods.append(method)
        if gen_action:
            action_source = inspect.getsource(enum)
        else:
            action_source = ""
        prefix = base_class_name.replace('Action', '').lower()
        class_template = f"""
{action_source}

class {prefix.title()}Callback(ActionMixin, CallbackData, prefix="{prefix}"):
    action: Action | {base_class_name}
{"".join(methods)}
    """
        template += class_template.strip() + "\n\n\n"
    return template.strip() + "\n"


# generated_code = generate_class_code(
#     AdminAction
# )
# path = r"G:\CodeProjects\PycharmProjects\AiogramProjectTemplate\project\src\apps\bot\callback_data\admin.py"
# Path(path).write_text(generated_code, "utf-8")

def generate_all_callbacks(action_name: str = "Action"):
    # Получаем список всех actions из файла actions.py
    actions = [obj for name, obj in inspect.getmembers(sys.modules[__name__]) if
               inspect.isclass(obj) and issubclass(obj, StrEnum)]
    # filter out all Action classes
    actions = [action for action in actions if action_name in action.__name__]

    # Для каждого action генерируем Callback и сохраняем в новый модуль
    for action in actions:
        module_name = action.__name__.replace('Action', '').lower()
        callback_path = BASE_DIR / f"src/apps/bot/callback_data/{module_name}.py"
        # if callback_path.exists():
        #     print(f"Callback module {module_name} already exists")
        #     continue
        callback_code = generate_class_code(action, gen_action=False)
        callback_path.write_text(callback_code, "utf-8")


def main():
    generate_all_callbacks()


if __name__ == '__main__':
    main()

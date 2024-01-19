import inspect
from enum import Enum, StrEnum
from pathlib import Path

from src.apps.bot.callback_data.actions import (
AdminAction,
)

imports = """
from aiogram import F
from aiogram.filters.callback_data import CallbackData
from enum import StrEnum
from .mixins import ActionMixin
"""




def generate_class_code(*action_enums: type[StrEnum], gen_action:bool = False):
    template = f"""
{imports}
"""
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
        prefix  = base_class_name.replace('Action', '').lower()
        class_template = f"""
{action_source}

class {prefix.title()}Callback(ActionMixin, CallbackData, prefix="{prefix}"):
    action: {base_class_name}
{"".join(methods)}
    """
        template += class_template.strip()+"\n\n\n"
    return template.strip()+"\n"


generated_code = generate_class_code(
    AdminAction
)
path = r"G:\CodeProjects\PycharmProjects\AiogramProjectTemplate\project\src\apps\bot\callback_data\admin.py"
Path(path).write_text(generated_code, "utf-8")
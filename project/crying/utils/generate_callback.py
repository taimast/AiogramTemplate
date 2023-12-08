import inspect
from enum import Enum, StrEnum
from pathlib import Path

from kwork_ffhashimov.apps.bot.callback_data.manager.actions import (
AssistantAction,
TaxiAction,
OtherAction,
MortgageAction,
ManagerAction,
LawyerAction,
)

imports = """
from aiogram import F
from aiogram.filters.callback_data import CallbackData
from enum import StrEnum
from .mixins import ActionMixin
"""




def generate_class_code(*action_enums: StrEnum):
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
        action_source = inspect.getsource(enum)
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
    AssistantAction,
    TaxiAction,
    OtherAction,
    MortgageAction,
    ManagerAction,
    LawyerAction,
)
Path("manager.py").write_text(generated_code, "utf-8")
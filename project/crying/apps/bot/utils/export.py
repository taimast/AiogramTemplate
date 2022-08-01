from aiogram.types import BufferedInputFile
from tortoise.contrib.pydantic import pydantic_queryset_creator, PydanticListModel

from project.crying.db.models import User

fields_nums = {
    "user_id": "1",
    "username": "2",
    "first_name": "3",
    "last_name": "4",
}


def parse_user_fields(fields_text: str) -> tuple:
    if "0" in fields_text:
        return ()
    else:
        return tuple(filter(lambda x: fields_nums[x] in fields_text, fields_nums))


async def export_users(_fields: tuple[str], _to: str) -> BufferedInputFile | str:
    UserPydanticList = pydantic_queryset_creator(User, include=_fields)
    users: PydanticListModel = await UserPydanticList.from_queryset(User.all())
    if _to == "text":
        users_list = list(users.dict()["__root__"])
        user_value_list = list(map(lambda x: str(list(x.values())), users_list))
        result = "\n".join(user_value_list)
    elif _to == "txt":
        users_list = list(users.dict()["__root__"])
        user_value_list = list(map(lambda x: str(list(x.values())), users_list))
        user_txt = "\n".join(user_value_list)
        result = BufferedInputFile(bytes(user_txt, "utf-8"), filename="users.txt")
    else:
        # json.dumps(ensure_ascii=False, default=str)
        result = BufferedInputFile(bytes(users.json(ensure_ascii=False), "utf-8"),
                                   filename="users.json")
    return result

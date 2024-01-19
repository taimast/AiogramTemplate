from typing import Protocol


class ChatProtocol(Protocol):
    id: int
    type: str
    username: str
    first_name: str
    last_name: str


def get_chat_name(chat: ChatProtocol) -> str:
    if chat.first_name and chat.last_name:
        return f"{chat.first_name} {chat.last_name}"
    elif chat.first_name:
        return chat.first_name
    elif chat.last_name:
        return chat.last_name
    elif hasattr(chat, "title"):
        return chat.title
    elif chat.username:
        return f"@{chat.username}"
    else:
        f"id{chat.id}"

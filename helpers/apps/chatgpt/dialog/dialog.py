from dataclasses import dataclass, field
from itertools import islice
from typing import TypedDict

import tiktoken
from loguru import logger

from .message import Message, Role


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logger.warning("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        # logger.warning("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        # logger.warning("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


class MessageTypedDict(TypedDict):
    role: str
    content: str
    name: str


@dataclass
class Dialog:
    messages: list[MessageTypedDict] = field(default_factory=list)

    def num_tokens(self, model="gpt-3.5-turbo"):
        return num_tokens_from_messages(self.messages, model=model)

    def iter_messages(self, reverse=False, limit=None):
        """Iterate over messages in the dialog."""
        messages = self.messages if not reverse else reversed(self.messages)
        if limit is not None:
            messages = islice(messages, limit)
        for message in messages:
            yield Message.from_dict(message)

    def add_message(self, message: Message):
        """Add a message to the dialog."""
        self.messages.append(message.to_dict())

    def add_system_message(self, text: str):
        """Add a system message to the dialog."""
        self.add_message(Message(role=Role.SYSTEM, content=text))

    def add_user_message(self, text: str):
        """Add a user message to the dialog."""
        self.add_message(Message(role=Role.USER, content=text))

    def add_assistant_message(self, text: str):
        """Add an assistant message to the dialog."""
        self.add_message(Message(role=Role.ASSISTANT, content=text))

    def get_last_content(self):
        """Get the content of the last message in the dialog."""
        return self.messages[-1]["content"]

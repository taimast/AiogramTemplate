import asyncio
import inspect
import queue
from collections.abc import Coroutine
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Awaitable, Self, TypeAlias, TypedDict, Union
from typing import Callable

from loguru import logger
from pydantic import AnyUrl
from pyrogram import Client as _Client
from pyrogram import enums
from pyrogram.client import log
from pyrogram.enums import ParseMode
from pyrogram.errors import BadRequest, SessionPasswordNeeded
from pyrogram.types import TermsOfService, User
from pyrogram.utils import ainput

__all__ = (
    "Client",
    "Proxy",
    "ProxyDict",
    "Autofill",
)

# common type for values in Client class
ClientValue: TypeAlias = Union[str, asyncio.Queue, queue.Queue]
Autofill: TypeAlias = Union[
    ClientValue,
    Callable[[], ClientValue],
    Callable[[], Awaitable[ClientValue]],
    Coroutine[Any, Any, ClientValue],
]
ProxyType: TypeAlias = Union[str, "ProxyDict", "Proxy", AnyUrl]


class ProxyDict(TypedDict):
    # "socks4", "socks5" and "http" are supported
    scheme: str
    hostname: str
    port: int
    username: str
    password: str


@dataclass
class Proxy:
    scheme: str
    hostname: str
    port: int | str
    username: str = None
    password: str = None

    def to_dict(self) -> ProxyDict:
        return self.__dict__

    @classmethod
    def from_url(cls, url: str) -> Self:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return cls(
            scheme=parsed.scheme,
            hostname=parsed.hostname,
            port=parsed.port,
            username=parsed.username,
            password=parsed.password
        )

    @classmethod
    def parse_proxy(cls, proxy: ProxyType) -> ProxyDict:
        if isinstance(proxy, Proxy):
            proxy = proxy.to_dict()
        elif isinstance(proxy, AnyUrl):
            proxy = Proxy(
                scheme=proxy.scheme,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.user,
                password=proxy.password
            ).to_dict()
        elif isinstance(proxy, str):
            proxy = Proxy.from_url(proxy).to_dict()
        return proxy


class Client(_Client):

    def __init__(self,
                 name: Path | str = None,
                 phone_number: Autofill = None,
                 phone_code: Autofill = None,
                 password: Autofill = None,
                 proxy: ProxyType = None,
                 timeout: int = 60,
                 **kwargs):
        name = name or f"{kwargs.get('api_id')}_{phone_number}"
        proxy: dict = Proxy.parse_proxy(proxy) if proxy else None
        self._attribute_cache = {}
        self._timeout = timeout
        super().__init__(
            name=name,
            phone_number=phone_number,
            phone_code=phone_code,
            password=password,
            proxy=proxy,
            parse_mode=ParseMode.HTML,
            **kwargs
        )

    async def set_unfilled_attribute(self, attr_name: str) -> ClientValue | None:
        async with asyncio.timeout(self._timeout):
            return await self._set_unfilled_attribute(attr_name)

    async def _set_unfilled_attribute(self, attr_name: str) -> ClientValue | None:
        attr = getattr(self, attr_name, None)
        if attr is None:
            return None
        logger.info(f"attr: {attr}")
        if cache_attr := self._attribute_cache.get(attr_name):
            if isinstance(cache_attr, (str, int)):
                return None
            attr = cache_attr

        while (inspect.isfunction(attr)
               or inspect.iscoroutinefunction(attr)
               or inspect.isawaitable(attr)):
            self._attribute_cache.setdefault(attr_name, attr)
            if inspect.iscoroutinefunction(attr):
                attr = await attr()
            elif inspect.isawaitable(attr):
                attr = await attr
            elif inspect.isfunction(attr):
                attr = await asyncio.to_thread(attr)

        if isinstance(attr, (str, int)):
            attr = attr

        elif isinstance(attr, asyncio.Queue):
            val = await attr.get()
            attr.task_done()
            attr = val
        elif isinstance(attr, queue.Queue):
            val = await asyncio.to_thread(attr.get)
            attr.task_done()
            attr = val
        return attr

    async def authorize(self) -> User:
        if self.bot_token:
            return await self.sign_in_bot(self.bot_token)

        while True:
            try:
                self.phone_number = await self.set_unfilled_attribute("phone_number")
                if not self.phone_number:
                    while True:
                        value = await ainput("Enter phone number or bot token: ")

                        if not value:
                            continue

                        confirm = (await ainput(f'Is "{value}" correct? (y/N): ')).lower()

                        if confirm == "y":
                            break

                    if ":" in value:
                        self.bot_token = value
                        return await self.sign_in_bot(value)
                    else:
                        self.phone_number = value

                sent_code = await self.send_code(self.phone_number)
            except BadRequest as e:
                print(e.MESSAGE)
                self.phone_number = None
                self.bot_token = None
            else:
                break

        sent_code_descriptions = {
            enums.SentCodeType.APP: "Telegram app",
            enums.SentCodeType.SMS: "SMS",
            enums.SentCodeType.CALL: "phone call",
            enums.SentCodeType.FLASH_CALL: "phone flash call"
        }

        print(f"The confirmation code has been sent via {sent_code_descriptions[sent_code.type]}")

        while True:
            self.phone_code = await self.set_unfilled_attribute("phone_code")
            if not self.phone_code:
                self.phone_code = await ainput("Enter confirmation code: ")

            try:
                signed_in = await self.sign_in(self.phone_number, sent_code.phone_code_hash, self.phone_code)
            except BadRequest as e:
                print(e.MESSAGE)
                self.phone_code = await self.set_unfilled_attribute("phone_code")
            except SessionPasswordNeeded as e:
                print(e.MESSAGE)

                while True:
                    print("Password hint: {}".format(await self.get_password_hint()))
                    self.password = await self.set_unfilled_attribute("password")
                    if not self.password:
                        self.password = await ainput("Enter password (empty to recover): ", hide=self.hide_password)

                    try:
                        if not self.password:
                            confirm = await ainput("Confirm password recovery (y/n): ")

                            if confirm == "y":
                                email_pattern = await self.send_recovery_code()
                                print(f"The recovery code has been sent to {email_pattern}")

                                while True:
                                    recovery_code = await ainput("Enter recovery code: ")

                                    try:
                                        return await self.recover_password(recovery_code)
                                    except BadRequest as e:
                                        print(e.MESSAGE)
                                    except Exception as e:
                                        log.error(e, exc_info=True)
                                        raise
                            else:
                                self.password = None
                        else:
                            return await self.check_password(self.password)
                    except BadRequest as e:
                        print(e.MESSAGE)
                        self.password = await self.set_unfilled_attribute("password")
            else:
                break

        if isinstance(signed_in, User):
            return signed_in

        while True:
            first_name = await ainput("Enter first name: ")
            last_name = await ainput("Enter last name (empty to skip): ")

            try:
                signed_up = await self.sign_up(
                    self.phone_number,
                    sent_code.phone_code_hash,
                    first_name,
                    last_name
                )
            except BadRequest as e:
                print(e.MESSAGE)
            else:
                break

        if isinstance(signed_in, TermsOfService):
            print("\n" + signed_in.text + "\n")
            await self.accept_terms_of_service(signed_in.id)

        return signed_up

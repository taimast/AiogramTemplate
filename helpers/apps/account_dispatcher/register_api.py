import asyncio
import random
import string
from queue import Queue
from time import sleep
from typing import Callable, Awaitable

from auto_selenium import Browser, by, ProxyMixin
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


class TelegramApiRegistrator(Browser, ProxyMixin):

    def create_driver(self):
        service = Service(**self.settings.dict(by_alias=True, exclude={"implicit_wait"}))
        for arg in self.args.get_args():
            self.options.add_argument(arg)
        if self.proxy:
            self.set_proxy()
        self.driver = webdriver.Chrome(service=service, options=self.options)
        self.driver.implicitly_wait(self.settings.implicit_wait)
        return self.driver

    def send_tg_code(self, phone):
        self.fe(by.id, "my_login_phone").send_keys(phone)
        self.fe(by.css_selector, ".btn.btn-primary.btn-lg").click()

    def enter_tg_code_get_api(self, code) -> tuple[str, str]:
        self.fe(by.id, "my_password").send_keys(code)
        # self.fes(by.css_selector, ".btn.btn-primary.btn-lg")[1].click()
        self.fe(by.xpath, "//button[text()='Sign In']").click()
        sleep(1)
        self.get("https://my.telegram.org/apps")

        app_title_elem = self.fe(by.id, "app_title")
        app_title_elem.clear()
        app_title_elem.send_keys(random.sample(string.ascii_lowercase, 15))
        app_shortname_elem = self.fe(by.id, "app_shortname")
        app_shortname_elem.clear()
        app_shortname_elem.send_keys(random.sample(string.ascii_lowercase, 15))
        self.fe(by.css_selector, ".btn.btn-primary").click()
        data_elems = self.fes(by.css_selector, ".form-control.input-xlarge.uneditable-input")
        api_id = data_elems[0].text.strip()
        api_hash = data_elems[1].text.strip()
        return api_id, api_hash

    def register(self, phone: str, cb: Callable[[], Queue]):
        self.get("https://my.telegram.org/auth")
        self.send_tg_code(phone)
        queue = cb()
        code = queue.get()
        api_id, api_hash = self.enter_tg_code_get_api(code)
        queue.put((api_id, api_hash))

    def input_register(self, phone: str | None = None):
        self.get("https://my.telegram.org/auth")
        if phone is None:
            phone = input("Введите номер телефона: ")
        self.send_tg_code(phone)
        code = input("Введите код: ")
        api_id, api_hash = self.enter_tg_code_get_api(code)
        print(f"api_id: {api_id}\napi_hash: {api_hash}")

    async def async_register(self, phone: str, cb: Awaitable[asyncio.Queue], timeout=60):
        await asyncio.to_thread(self.__enter__)
        try:
            await asyncio.to_thread(self.get, "https://my.telegram.org/auth")
            await asyncio.to_thread(self.send_tg_code, phone)
            queue = await cb
            async with asyncio.timeout(timeout):
                code = await queue.get()
            api_id, api_hash = await asyncio.to_thread(self.enter_tg_code_get_api, code)
            return api_id, api_hash
        finally:
            self.__exit__(None, None, None)


def main():
    with TelegramApiRegistrator() as registrator:
        try:
            registrator.input_register("+7 707 684 51 18")
        except Exception as e:
            logger.exception(e)
        finally:
            print("exiting")
            sleep(100)


if __name__ == '__main__':
    main()

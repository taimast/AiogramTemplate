import asyncio
from asyncio import TaskGroup
from enum import Enum
from pprint import pprint

from loguru import logger
from pydantic import BaseModel

from project.crying.config.logg_settings import init_logging
from project.crying.config.merchant.crypto_cloud import CryptoCloud, CryptoInvoiceRequest
from project.crying.config.merchant.yookassa import Yookassa


class Level(str, Enum):
    # 5
    TRACE = "TRACE"
    # 10
    DEBUG = "DEBUG"
    # 20
    INFO = "INFO"
    # 25
    SUCCESS = "SUCCESS"
    # 30
    WARNING = "WARNING"
    # 40
    ERROR = "ERROR"
    # 50
    CRITICAL = "CRITICAL"


class Some(BaseModel):
    level: Level
    stream: bool = True
    write: bool = True
    base_logger: bool = True
# long name for function
def long_name_for_function():
    logger.warning("Hello, world!")

def some_long_name():
    logger.critical("Hello, world! Critical")


def main():
    s = Some(level=Level.INFO, stream=True, write=True, base_logger=True)
    init_logging(s.level)
    logger.info("Hello, world!")
    long_name_for_function()
    some_long_name()

async def main2():
    c = CryptoCloud(api_key=1234, _session=None, shop_id=1234)
    pprint(c.dict())
    await c.get_session()
    # await c.close_session()
async def main4():
    c = CryptoInvoiceRequest(amount=1, currency="RUB",  order_id="1234")
    pprint(c.dict())
    # await c.close_session()
async def main3():
    # c = Yookassa(shop_id="SrL65kqO7lp3bhCt",
    #                 api_key="***REMOVED***")
    # c = Yookassa(shop_id="878719",
    #             api_key="***REMOVED***")
    c = Yookassa(shop_id="886879",
                api_key="***REMOVED***")
    # c = Yookassa(shop_id="886927",
    #             api_key="***REMOVED***")

    # c2 = Yookassa(shop_id="878719",
    #             api_key="***REMOVED***")

    # res = await c.create_invoice(amount=1, currency="RUB", order_id="1234")

    tasks = []
    for i in range(10):
        tasks.append(c.create_invoice(amount=1, currency="RUB"))
            # await tg.spawn(c2.create_invoice, amount=1, currency="RUB", order_id="1234")
    invoices = await asyncio.gather(*tasks)
    invoices_ids = [i.id for i in invoices]
    pprint(len(invoices_ids))
    pprint(len(set(invoices_ids)))

    # await c.close_session()
    # return
    while True:
        for i in invoices:
            pprint(await c.get_invoice(i.id))
        await asyncio.sleep(2)
    # c = CryptoInvoiceRequest(amount=1, currency="RUB",  order_id="1234")
    # pprint(c.dict())
    # await c.close_session()


async def main5():
    c = CryptoCloud(shop_id="SrL65kqO7lp3bhCt",
                    api_key="***REMOVED***")
    res =  await c.create_invoice(amount=1, currency="RUB", order_id="1234")
    pprint(res)


if __name__ == '__main__':
    # main2()
    asyncio.run(main3())

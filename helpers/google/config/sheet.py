import asyncio
from asyncio import Event
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from aiogoogle import Aiogoogle, GoogleAPI
from aiogoogle.auth.creds import ServiceAccountCreds
from loguru import logger
from shop_bot.apps.sheet.actions import drop_down_list, add_row, copy_from_cell
from shop_bot.config import BASE_DIR
from shop_bot.config.config import GoogleSheets
from shop_bot.db.models import Order


def load_yaml(file: str | Path) -> dict[str, Any] | list[Any]:
    with open(BASE_DIR / file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@dataclass
class OrderWorker:
    credentials: ServiceAccountCreds
    spreadsheet_id: str
    queue: asyncio.Queue[tuple[Order, Event]] = field(default_factory=asyncio.Queue)

    async def add_order(self, order: Order, event: Event):
        logger.info(f"Adding order {order.id} to queue")
        await self.queue.put((order, event))

    async def start(self):
        async with Aiogoogle(service_account_creds=self.credentials) as aiogoogle_client:
            sheet: GoogleAPI = await aiogoogle_client.discover('sheets', 'v4')
            logger.info("Starting order worker")
            while True:
                order, event = await self.queue.get()
                updated_row_id: int = await add_row(
                    aiogoogle_client,
                    sheet,
                    self.spreadsheet_id,
                    order.to_sheet()
                )
                await copy_from_cell(aiogoogle_client, sheet, self.spreadsheet_id, updated_row_id)
                logger.success(f"Added order {order.id} to sheet {updated_row_id}")
                self.queue.task_done()
                order.sheet_id = updated_row_id
                event.set()


async def main():
    google_sheets = GoogleSheets()
    # await new_product(google_sheets.credentials, google_sheets.spreadsheet_id, list(range(15)))
    # print(await new_product(google_sheets.credentials, google_sheets.spreadsheet_id, list(range(15))))
    # print(await new_product(google_sheets.credentials, google_sheets.spreadsheet_id, list(range(15))))

    async with Aiogoogle(service_account_creds=google_sheets.credentials) as aiogoogle_client:
        sheet: GoogleAPI = await aiogoogle_client.discover('sheets', 'v4')
        print(await drop_down_list(aiogoogle_client, sheet, google_sheets.spreadsheet_id))


if __name__ == '__main__':
    asyncio.run(main())

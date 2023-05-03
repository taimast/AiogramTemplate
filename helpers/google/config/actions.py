import re

from aiogoogle import Aiogoogle, GoogleAPI
from loguru import logger
from shop_bot.config.config import GoogleSheets


async def add_row(aiogoogle_client: Aiogoogle, sheet: GoogleAPI, spreadsheet_id: str, row: list) -> int:
    result = await aiogoogle_client.as_service_account(
        sheet.spreadsheets.values.append(
            spreadsheetId=spreadsheet_id,
            valueInputOption="USER_ENTERED",
            range='A1',
            json={
                'values': [row]
            }
        ))
    updated_row = re.match(r'.*!A(\d+):.*', result['updates']['updatedRange']).group(1)
    return int(updated_row)


# копировать из другой ячейки Правила проверки раскрывающийся список с 3 элемантами  Проверка, В работе и Готов в google sheets через api
async def copy_from_cell(aiogoogle_client: Aiogoogle, sheet: GoogleAPI, spreadsheet_id: str, destination_row: int):
    start_column = 1
    end_column = 2
    data_validation_request = {
        "copyPaste": {
            "source": {
                "sheetId": 0,  # Идентификатор листа
                "startRowIndex": 1,
                "endRowIndex": 2,  # Количество строк, на которые распространяется список
                "startColumnIndex": start_column,  # Начальный столбец, в котором будет расположен список
                "endColumnIndex": end_column,  # Конечный столбец, в котором будет расположен список
            },
            "destination": {
                "sheetId": 0,  # Идентификатор листа
                "startRowIndex": destination_row - 1,
                "endRowIndex": destination_row - 1,  # Количество строк, на которые распространяется список
                "startColumnIndex": start_column,  # Начальный столбец, в котором будет расположен список
                "endColumnIndex": end_column,  # Конечный столбец, в котором будет расположен список
            },
            "pasteType": "PASTE_NORMAL",
            "pasteOrientation": "NORMAL",
        },
    }
    result = await aiogoogle_client.as_service_account(
        sheet.spreadsheets.batchUpdate(
            spreadsheetId=spreadsheet_id,
            json={
                "requests": [data_validation_request]
            }
        ))
    return result


# Правила проверки раскрывающийся список с 3 элементами:
# Проверка, В работе и Готов со цветами красный, светложелтый, зеленый в google sheets через api v4
async def drop_down_list(aiogoogle_client: Aiogoogle, sheet: GoogleAPI, spreadsheet_id: str):
    request = {
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [
                    {
                        "sheetId": 0,
                        "startRowIndex": 1,
                        "endRowIndex": 2,
                        "startColumnIndex": 1,
                        "endColumnIndex": 2
                    }
                ],
                "booleanRule": {
                    "condition": {
                        "type": "CUSTOM_FORMULA",
                        "values": [
                            {
                                "userEnteredValue": "=OR(A2=\"Проверка\",A2=\"В работе\",A2=\"Готов\")"
                            }
                        ]
                    },
                    "format": {
                        "backgroundColor": {
                            "red": 1,
                            "green": 0,
                            "blue": 0
                        }
                    }
                }
            },
            "index": 0
        }
    }

    result = await aiogoogle_client.as_service_account(
        sheet.spreadsheets.batchUpdate(
            spreadsheetId=spreadsheet_id,
            json={
                "requests": [request]
            }
        ))

    return result


import asyncio


async def main():
    google_sheets = GoogleSheets()
    async with Aiogoogle(service_account_creds=google_sheets.credentials) as aiogoogle_client:
        sheet: GoogleAPI = await aiogoogle_client.discover('sheets', 'v4')
        row = await add_row(aiogoogle_client, sheet, google_sheets.spreadsheet_id,
                            ["04.03.2023", 'Проверка', 'В работе', 'Готов'])
        logger.info(f'Добавлена строка {row}')
        await copy_from_cell(aiogoogle_client, sheet, google_sheets.spreadsheet_id, row)
        # await drop_down_list(aiogoogle_client, sheet, google_sheets.spreadsheet_id)


if __name__ == '__main__':
    asyncio.run(main())

import json
from datetime import datetime
from decimal import Decimal

import aiofiles
from aiogram import types


def get_days_letters(data: str):
    # Преобразуйте строку в объект datetime
    received_date = datetime.strptime(data, "%d.%m.%Y")

    # Получите текущую дату
    current_date = datetime.now()

    # Вычислите разницу между текущей датой и полученной датой
    date_difference = current_date - received_date

    # Получите количество дней из объекта timedelta
    days_difference = date_difference.days

    return days_difference


async def get_bot_username(message: types.Message):
    bot_info = await message.bot.get_me()
    return bot_info.username


def format_number(number):
    """
    Форматирует числа: например из 5000 делает 5 000
    """

    formatted_number = "{:,}".format(number).replace(",", " ")
    return formatted_number


def subtract_percentage(number, percentage):
    """
    Вычитает проценты из числа
    """

    result = (Decimal(number) * Decimal(str(percentage))) / 100
    return round(result, 2)


async def read_json_file(filename):
    async with aiofiles.open(filename, mode='r') as file:
        content = await file.read()
        return content


async def write_json_file(filename, js):
    async with aiofiles.open(filename, mode='w') as file:
        await file.write(json.dumps(js, indent=4))

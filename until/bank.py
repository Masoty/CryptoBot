import json
from datetime import datetime, timedelta
from decimal import Decimal

from create_bot import bot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import asyncio

from db.db import session_db
from db.models import Person
from . import read_json_file, update_title, add_balance, update_refers_hierarchy


def get_firs_monday():
    now = datetime.now()

    next_day = now + timedelta(days=1)
    next_day = next_day.replace(hour=0, minute=0, second=0, microsecond=0)

    time_until_next_day = (next_day - now).total_seconds()

    today_week = datetime.now().weekday()

    return (6 - today_week) * 86400 + time_until_next_day

async def extract_week_rate():
    content = await read_json_file("data/config.json")
    data = json.loads(content)
    return data["week_rate"]


def rate_balance_bank_user(money: int, rate):
    result = (Decimal(money) * Decimal(str(rate))) / 100
    return round(result, 2)

@session_db
async def get_all_users(session: AsyncSession):
    return await Person.get_all_users_balance_bank(session)


@session_db
async def bank_updates_every_week(session: AsyncSession):
    time_sleep = get_firs_monday()

    # Ждем до следующего понедельника
    print(f"Sleep: {time_sleep}")
    await asyncio.sleep(time_sleep)
    print("Начисляем по копилке")

    # Получаем всех пользователей
    users = await Person.get_all_users_balance_bank(session)

    # Получаем недельный процент
    week_rate = await extract_week_rate()

    # Перебираем каждого пользователя
    for user in users:

        # Начисляем проценты от активного баланса копилки
        if user.balance_bank > 0:
            cl_rate_money = rate_balance_bank_user(user.balance_bank, week_rate)
            user.balance_bank = user.balance_bank + cl_rate_money
            user.balance_all_time_bank = user.balance_all_time_bank + cl_rate_money
            user.balance_all_time = user.balance_all_time + cl_rate_money
            await session.commit()

            # Распределяем процент между реферами
            if cl_rate_money > 0.00:
                await update_refers_hierarchy(user, cl_rate_money, session, bank_event=True)
                try:
                    await bot.send_message(user.user_id, text=f"<b>Вам в копилку начислено +{cl_rate_money} AS. Доходность за прошлою неделю в общем пуле составила {week_rate}%</b>", parse_mode="HTML")
                except:
                    pass

        # Если есть средства на недельном балансе, пора их пустить в работу для получения процентов, к основному балансу копилки
        if user.balance_buffer_bank:
            user.balance_bank = user.balance_bank + user.balance_buffer_bank
            user.balance_buffer_bank = 0

        # Обновляем статус, если он заслуживает
        await update_title(user, session)

        await session.commit()

    await bank_updates_every_week()





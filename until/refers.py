from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from create_bot import bot
from db.db import session_db
from db.models import Person
from . import subtract_percentage, update_title


async def minus_balance(message: types.Message, number: int, session: AsyncSession):

    """
    Вычитает суму за траты в боте, и также распределяет проценты между реферами
    """

    person = await Person.obj(message.chat.id, session)
    person.balance = person.balance - number
    await session.commit()

    # Добавляем реферам проценты от покупки
    await update_refers_hierarchy(person, number, session)

    # Добавляем реферам в общий оборот
    await update_all_refers_hierarchy(person.refer, number, session)


async def add_balance(user_id: int, number: int, session: AsyncSession):

    """
    Добавляет баланс в боте за копилку, и также распределяет проценты между реферами
    """

    person = await Person.obj(user_id, session)
    person.balance = person.balance + number
    person.balance_all_time = person.balance_all_time + number
    await session.commit()

    # Добавляем реферам проценты от покупки
    await update_refers_hierarchy(person, number, session)

@session_db
async def add_packet_rub(user_id: int, number: int, session: AsyncSession):

    """
    Добавляет реферам процент от покупки пакета за рубли
    """

    person = await Person.obj(user_id, session)

    # Добавляем реферам проценты от покупки
    await update_refers_hierarchy(person, number, session)

    # Добавляем реферам в общий оборот
    await update_all_refers_hierarchy(person.refer, number, session)

    # Обновляем статус
    await update_title(person, session)


async def update_refers_hierarchy(person: Person, number: int, session: AsyncSession, bank_event: bool = False):

    """
    Добавляет проценты реферам от покупки их реферала, 5 уровней

    :param person: Person
    :param number сума покупки реферала
    :param session сессия
    :param bank_event - Указать, ето банк, или нет, ибо банк не учитывает первую линию
    """

    refer = person.refer

    refers = {}

    # Вытягиваем 5 реферов из цепочки реферов
    for x in range(5):
        refer_person = await Person.obj(refer, session)
        refers[refer] = refer_person.packet
        refer = refer_person.refer

        # Если дошли до самого первого рефера, родоначальника, то останавливаем подщет
        if refer == 0:
            break

    # До какого уровня достает каждый пакет
    stage_packets = {
        "FREE": 0,
        "LITE": 1,
        "PRO": 2,
        "VIP": 4
    }

    for refer in refers:
        refer_person = await Person.obj(refer, session)

        # Указать сколько процентов заслуживает каждый рефер
        if list(refers.keys())[0] == refer:
            num_percent = subtract_percentage(number, 10)
            if not bank_event:
                refer_person.turnover_first_line = refer_person.turnover_first_line + number
        else:
            num_percent = subtract_percentage(number, 5)

        # Если действие пакета рефера достает до уровня реф. системы на которой находиться реферал, то добавляем проценты
        if stage_packets[refer_person.packet] >= list(refers.keys()).index(refer):

            # Обновляем информацию о балансах
            refer_person.balance = refer_person.balance + num_percent
            refer_person.balance_all_time = refer_person.balance_all_time + num_percent
            refer_person.balance_all_time_partner = refer_person.balance_all_time_partner + num_percent

            # Присылает сообщение о процентах
            try:
                await bot.send_message(refer_person.user_id, f"💰 Вам засчитано {num_percent} AS с вашего реферала {list(refers).index(refer)+1} уровня (@{person.username})")
            except: pass

            # Обновляем статус, если он заслуживает
            await update_title(refer_person, session)

            # Сохраняем данные
            await session.commit()


async def update_all_refers_hierarchy(refer: int, number: int, session: AsyncSession):


    while True:
        # Если дошли до самого первого рефера, родоначальника, то останавливаем подщет
        if refer == 0:
            break

        # Обновляем общий оборот всех реферов до самого первого (любой глубины)
        refer_person = await Person.obj(refer, session)
        refer_person.total_turnover = refer_person.total_turnover + number
        await update_title(refer_person, session)
        await session.commit()

        refer = refer_person.refer


async def register_refers_line(message: types.Message, session: AsyncSession):
    person = await Person.obj(message.chat.id, session)
    refer = person.refer

    refers = {}

    # Вытягиваем 5 реферов из цепочки реферов
    for x in range(5):
        refer_person = await Person.obj(refer, session)
        refers[refer] = refer_person.packet

        if len(refers) == 1:
            refer_person.one_line_referrals = refer_person.one_line_referrals + 1
        if len(refers) == 2:
            refer_person.two_line_referrals = refer_person.two_line_referrals + 1
        if len(refers) == 3:
            refer_person.three_line_referrals = refer_person.three_line_referrals + 1
        if len(refers) == 4:
            refer_person.four_line_referrals = refer_person.four_line_referrals + 1
        if len(refers) == 5:
            refer_person.five_line_referrals = refer_person.five_line_referrals + 1

        await session.commit()


        text = f"""
🔥 У вас новый реферал на {len(refers)} уровне - @{message.from_user.username}
        """

        try: await bot.send_message(refer_person.user_id, text=text)
        except: pass

        refer = refer_person.refer

        # Если дошли до самого первого рефера, родоначальника, то останавливаем подщет
        if refer == 0:
            break






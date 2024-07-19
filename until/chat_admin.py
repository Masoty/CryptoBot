import io
import json

import openpyxl
from aiogram import types
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.admin import AdminButtons
from data.config import admins
from db.db import session_db
from db.models import Person, Events
from until import extract_week_rate, read_json_file, write_json_file


async def leave_balance_false(message: types.Message, user_id: int, money: int, session: AsyncSession):
    text = message.text + "\n\n❌ Вывод отменен"

    await message.delete()

    await message.answer(text)

    await message.bot.send_message(user_id, f"❌ Отказано в выводе, ваши {money} AS возвращены вам на баланс")

    person = await Person.obj(user_id, session)

    person.balance = person.balance + money

    await session.commit()


async def leave_balance_true(message: types.Message, user_id: int, money: int):
    text = str(message.text) + "\n\n✅ Выведено"

    await message.delete()

    await message.answer(text)

    await message.bot.send_message(user_id,
                                   f"✅ Ваша заявка на вывод {money} AS была удовлетворена, деньги выведены на указанный адрес")


async def leave_balance_bank_false(message: types.Message, user_id: int, money: int, session: AsyncSession):
    text = message.text + "\n\n❌ Вывод отменен"

    await message.delete()

    await message.answer(text)

    await message.bot.send_message(user_id,
                                   f"❌ Отказано в выводе из копилки, ваши {money} AS возвращены вам на баланс копилки")

    person = await Person.obj(user_id, session)

    person.balance_buffer_bank = person.balance_buffer_bank + money

    await session.commit()


async def leave_balance_bank_true(message: types.Message, user_id: int, money: int, session: AsyncSession):
    text = message.text + "\n\n✅ Выведено"

    await message.delete()

    await message.answer(text)

    await message.bot.send_message(user_id,
                                   f"✅ Ваша заявка на вывод {money} AS из копилки была удовлетворена, деньги выведены на кошелек")

    person = await Person.obj(user_id, session)

    person.balance = person.balance + money

    await session.commit()


@session_db
async def get_all_users(message: types.Message, session: AsyncSession):
    if message.chat.id not in admins:
        return

    all_users = await Person.get_all_users_balance_bank(session)

    buffer = io.BytesIO()

    wb = openpyxl.Workbook()

    sheet = wb.active

    row = 2
    sheet["A1"] = "UserID"
    sheet["B1"] = "Имя"
    sheet["C1"] = "Username"
    sheet["D1"] = "Телефон"
    sheet["E1"] = "Город"
    sheet["F1"] = "Дата регистрации"
    sheet["G1"] = "Пакет"
    sheet["H1"] = "ReferID"
    sheet["I1"] = "Баланс"
    sheet["J1"] = "Личный баланс за все время"
    sheet["K1"] = "Баланс Банки"
    sheet["L1"] = "Заработано с банки"
    sheet["M1"] = "Заработано с партнерки"
    sheet["N1"] = "Звание"
    sheet["O1"] = "Оборот первой линии"
    sheet["P1"] = "Общий оборот рефералов"
    sheet["Q1"] = "Кол-во рефералов 1 линии"
    sheet["R1"] = "Кол-во рефералов 2 линии"
    sheet["S1"] = "Кол-во рефералов 3 линии"
    sheet["T1"] = "Кол-во рефералов 4 линии"
    sheet["U1"] = "Кол-во рефералов 5 линии"

    for person in all_users:
        sheet[row][0].value = person.user_id
        sheet[row][1].value = person.first_name
        sheet[row][2].value = f"@{person.username}"
        sheet[row][3].value = person.phone
        sheet[row][4].value = person.city
        sheet[row][5].value = person.data_register
        sheet[row][6].value = person.packet
        sheet[row][7].value = person.refer
        sheet[row][8].value = person.balance
        sheet[row][9].value = person.balance_all_time
        sheet[row][10].value = person.balance_bank + person.balance_buffer_bank
        sheet[row][11].value = person.balance_all_time_bank
        sheet[row][12].value = person.balance_all_time_partner
        sheet[row][13].value = person.status
        sheet[row][14].value = person.turnover_first_line
        sheet[row][15].value = person.total_turnover
        sheet[row][16].value = person.one_line_referrals
        sheet[row][17].value = person.two_line_referrals
        sheet[row][18].value = person.three_line_referrals
        sheet[row][19].value = person.four_line_referrals
        sheet[row][20].value = person.five_line_referrals
        row = row + 1

    wb.save(buffer)
    buffer.seek(0)

    file = types.InputFile(buffer, filename="result.xlsx")
    await message.answer_document(file)


async def procent(message: types.Message):
    if message.chat.id not in admins:
        return

    procent_number = await extract_week_rate()

    text = f"""
    📌 Процент ставки в копилке: {procent_number}%
    """

    markup = AdminButtons.procent()

    await message.answer(text, reply_markup=markup)


async def edit_procent(message: types.Message, state: FSMContext):
    await message.edit_text("✏ Введите новый процент")
    await state.set_state("edit_procent_commit")


async def edit_procent_commit(message: types.Message, state: FSMContext):
    try:
        float(message.text)
    except:
        await message.answer("❌ Нужно вводить числом, попробуйте еще раз")
        return

    await state.finish()

    js = json.loads(await read_json_file("data/config.json"))
    js["week_rate"] = float(message.text)
    await write_json_file("data/config.json", js)

    await message.answer("✅ Процент изменен")


@session_db
async def get_events_users(message: types.Message, session: AsyncSession):
    if message.chat.id not in admins:
        return

    all_events = await Events.get_events(session)

    for event in all_events:

        buffer = io.BytesIO()

        wb = openpyxl.Workbook()

        sheet = wb.active

        row = 2
        sheet["A1"] = "UserID"
        sheet["B1"] = "Имя"
        sheet["C1"] = "Username"
        sheet["D1"] = "Телефон"

        for user in event.users:
            person = await Person.obj(user, session)

            sheet[row][0].value = person.user_id
            sheet[row][1].value = person.first_name
            sheet[row][2].value = f"@{person.username}"
            sheet[row][3].value = person.phone
            row = row + 1

        wb.save(buffer)
        buffer.seek(0)

        file = types.InputFile(buffer, filename=f"{event.name}.xlsx")
        await message.answer_document(file)


async def send_all_users(message: types.Message, state: FSMContext):

    if message.chat.id not in admins:
        return

    await message.answer("✏ Введите сообщение для отправки всем пользователям бота\n/CANCEL - для отмены")
    await state.set_state("send_all_users_commit")


@session_db
async def send_all_users_commit(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.finish()

    if message.text == "/CANCEL":
        await message.answer("❌ Рассылка отменена")
        return

    text = message.text

    persons = await Person.get_all_users_balance_bank(session)
    commits = 0

    for user in persons:
        try:
            if message.photo:
                await message.bot.send_photo(chat_id=user.user_id, photo=message.photo[-1].file_id, caption=message.caption, parse_mode="HTML")
            else:
                await message.bot.send_message(user.user_id, text, parse_mode="HTML")
            commits += 1
        except: pass

    await message.answer(f"✅ Отправлено {commits} пользователям")


import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.buttons import Button
from data.texts import *
from db.db import session_db
from db.models import Person
from fun import *
from fun.view import menu, hello, write_wallet, leave_money_true, leave_money_not_balance, bank, bank_add_true, \
    add_bank_not_balance, add_bank_incorrect, leave_bank_incorrect, bank_leave_true, leave_bank_not_balance, information
from until.crypto import check_user_pay, create_invoice


@session_db
async def write_number(message: types.Message, state: FSMContext, session: AsyncSession):
    # Проверяем отправил ли пользователь номер
    if message.content_type == "contact":
        phone = message.contact.phone_number

        # Сохраняем номер телефона
        person = await Person.obj(message.chat.id, session)
        person.phone = phone
        await session.commit()
        await state.finish()
        await user_agreement(message)
    else:
        await message.answer("🔰 Пожалуйста, отправьте номер телефона", reply_markup=Button.send_number())


@session_db
async def about_your_country_commit(message: types.Message, state: FSMContext, session: AsyncSession):
    # Проверяем отправил ли пользователь текст
    if message.content_type == "text":
        city = message.text

        # Сохраняем номер телефона
        person = await Person.obj(message.chat.id, session)
        person.city = city
        await session.commit()
        await state.finish()
        await hello(message)
    else:
        await message.answer("✏ Пожалуйста, укажите с какого вы города/страны")

@session_db
async def edit_city_commit(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.content_type == "text":
        city = message.text

        # Сохраняем номер телефона
        person = await Person.obj(message.chat.id, session)
        person.city = city
        await session.commit()
        await state.finish()
        await information(message, edit=False)
    else:
        await message.answer("✏ Пожалуйста, укажите с какого вы города/страны")


@session_db
async def leave_money_commit(message: types.Message, state: FSMContext, session: AsyncSession):

    if message.text.isnumeric():
        person = await Person.obj(message.chat.id, session)
        if person.balance < 50:
            await state.finish()
            await message.answer(leave_money_commit_text)
            await menu(message)
            return
        if int(message.text) < 50:
            return await message.answer(leave_money_50_minimum_text)
        if person.balance < int(message.text):
            await state.finish()
            return await leave_money_not_balance(message)
        else:
            await state.update_data(money=int(message.text))
            await write_wallet(message, state)
    else:
        await state.finish()
        await message.answer(leave_money_wallet_error_text)
        await menu(message)


@session_db
async def write_wallet_commit(message: types.Message, state: FSMContext, session: AsyncSession):


    if message.text == "❌ Отмена":
        await state.finish()
        await menu(message)
    else:

        data = await state.get_data()

        money = data.get("money")
        wallet = message.text

        person = await Person.obj(message.chat.id, session)
        person.balance = person.balance - money
        await session.commit()

        await state.finish()
        await leave_money_true(message, money, wallet, session)


async def add_money_commit(message: types.Message, state: FSMContext):
    await state.finish()

    try:
        int(message.text)

        if int(message.text) < 0:
            raise TypeError

        if int(message.text) < 10:
            raise IndexError
    except IndexError:
        await message.answer("❌ Минимальная сумма пополнения 10 USDT")
        await menu(message)
        return
    except Exception:
        await message.answer("❌ Не корректно указанное число")
        await menu(message)
        return


    invoice = await create_invoice(int(message.text), f"Пополнение баланса в бота ASTERI CLUB на {message.text} AS")

    url = invoice["url"]

    print(message.text)
    print(url)

    asyncio.create_task(check_user_pay(message.chat.id, int(message.text), invoice["id"]))

    text = add_money_commit_text
    markup = await Button.add_money_commit(url)

    await message.answer_photo(photo=types.InputFile(f"data/photo/leave_money_true.jpg"), caption=text,
                               reply_markup=markup)




@session_db
async def add_bank_check(message: types.Message, state: FSMContext, session: AsyncSession):


    if message.text == "⬅ Назад":
        await state.finish()
        await message.answer(text="🚫 Отменено", reply_markup=types.ReplyKeyboardRemove())
        await bank(message, edit=False, session=session)
    else:
        if message.text.isnumeric():
            if int(message.text) < 10:
                return await add_bank_incorrect(message)

            person = await Person.obj(message.chat.id, session)
            if person.balance >= int(message.text):
                await state.finish()
                await bank_add_true(message, int(message.text))
            else:
                await state.finish()
                await add_bank_not_balance(message)
        else:
            await add_bank_incorrect(message)


@session_db
async def leave_bank_check(message: types.Message, state: FSMContext, session: AsyncSession):

    if message.text == "⬅ Назад":
        await state.finish()
        await message.answer(text="🚫 Отменено", reply_markup=types.ReplyKeyboardRemove())
        await bank(message, edit=False, session=session)
    else:
        if message.text.isnumeric():
            if int(message.text) < 50:
                return await leave_bank_incorrect(message)

            person = await Person.obj(message.chat.id, session)
            if person.balance_bank + person.balance_buffer_bank >= int(message.text):
                await state.finish()
                await bank_leave_true(message, int(message.text))
            else:
                await state.finish()
                await leave_bank_not_balance(message)
        else:
            await leave_bank_incorrect(message)

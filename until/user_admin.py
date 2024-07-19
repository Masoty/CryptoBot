from aiogram import types
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.admin import UserPanel
from data.config import admins, packets
from db.db import session_db
from db.models import Person
from fun.view import by_packet_view
from until import update_title


async def admin_panel_user(message: types.Message, user_id: str, session: AsyncSession, edit=False):
    """
    Админ панель
    """

    # Проверяем есть ли пользователь админом
    if message.chat.id not in admins:
        return

    # Корректный ли идентификатор
    if not user_id.isnumeric():
        return message.answer("❌ Не корректный id пользователя")

    user_id = int(user_id)

    # Зарегистрированный ли пользователь в базе
    if not await Person.is_register(user_id, session):
        return message.answer("❌ Такого пользователя нет в проекте")

    person = await Person.obj(user_id, session)

    text = f"""
👤 Личная информация
UserID: {person.user_id}
Имя: {person.first_name}
Username: @{person.username}
Телефон: {person.phone}
Город: {person.city}
Дата регистрации: {person.data_register}

🤖 Информация в боте
Пакет: {person.packet}
ReferID: {person.refer}

💰 Финансы 
Баланс: {person.balance} AS
Личный баланс за все время: {person.balance_all_time} AS
Баланс Банки: {person.balance_bank+person.balance_buffer_bank} AS
Заработано с банки: {person.balance_all_time_bank} AS
Заработано с партнерки: {person.balance_all_time_partner} AS

👥 Партнерская программа 
Звание: {person.status}

Оборот первой линии: {person.turnover_first_line} AS
Общий оборот рефералов: {person.total_turnover} AS

Кол-во рефералов 1 линии: {person.one_line_referrals}
Кол-во рефералов 2 линии: {person.two_line_referrals}
Кол-во рефералов 3 линии: {person.three_line_referrals}
Кол-во рефералов 4 линии: {person.four_line_referrals}
Кол-во рефералов 5 линии: {person.five_line_referrals}
    
    """

    markup = UserPanel.panel(user_id)

    if edit:
        await message.edit_text(text, reply_markup=markup)
    else:
        await message.answer(text, reply_markup=markup)


async def user_panel_add(message: types.Message, user_id: int, state: FSMContext):
    await message.edit_text("✏ Введите число на сколько вы хотите увеличить баланс\nНажмите /CANCEL для отмены")
    await state.update_data(user_id=user_id)
    await state.set_state("user_panel_add_commit")


@session_db
async def user_panel_add_commit(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.content_type == "text":

        data = await state.get_data()
        user_id = int(data['user_id'])

        if message.text == "/CANCEL":
            await message.answer("🚫 Отмена", reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
            await admin_panel_user(message, str(user_id), session)
        else:
            if not message.text.isnumeric():
                return await message.answer("❌ Не верный тип данных, попробуйте еще раз")

            person = await Person.obj(user_id, session)
            person.balance = person.balance + int(message.text)
            await session.commit()
            await message.bot.send_message(user_id, f"✅ Ваш баланс пополнен на +{message.text} AS командой ASTERI CLUB")
            await message.answer(f"✅ Баланс {person.first_name} пополнен на +{message.text} AS")
            await state.finish()
            await admin_panel_user(message, str(user_id), session)
    else:
        await message.answer("❌ Не верный тип данных, попробуйте еще раз")


async def user_panel_minus(message: types.Message, user_id: int, state: FSMContext):
    await message.edit_text("✏ Введите число на сколько вы хотите уменьшить баланс\nНажмите /CANCEL для отмены")
    await state.update_data(user_id=user_id)
    await state.set_state("user_panel_minus_commit")


@session_db
async def user_panel_minus_commit(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.content_type == "text":

        data = await state.get_data()
        user_id = int(data['user_id'])

        if message.text == "/CANCEL":
            await message.answer("🚫 Отмена", reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
            await admin_panel_user(message, str(user_id), session)
        else:
            if not message.text.isnumeric():
                return await message.answer("❌ Не верный тип данных, попробуйте еще раз")

            person = await Person.obj(user_id, session)
            person.balance = person.balance - int(message.text)
            await session.commit()
            await message.bot.send_message(user_id, f"♦ Ваш баланс уменьшен на {message.text} AS командой ASTERI CLUB")
            await message.answer(f"♦ Баланс {person.first_name} уменьшен на {message.text} AS")
            await state.finish()
            await admin_panel_user(message, str(user_id), session)
    else:
        await message.answer("❌ Не верный тип данных, попробуйте еще раз")


async def user_panel_bank_balance_add(message: types.Message, user_id: int, state: FSMContext):

    await message.edit_text("✏ Введите число на сколько вы хотите увеличить баланс копилки\nНажмите /CANCEL для отмены")
    await state.update_data(user_id=user_id)
    await state.set_state("user_panel_bank_add_commit")



@session_db
async def user_panel_bank_add_commit(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.content_type == "text":

        data = await state.get_data()
        user_id = int(data['user_id'])

        if message.text == "/CANCEL":
            await message.answer("🚫 Отмена", reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
            await admin_panel_user(message, str(user_id), session)
        else:
            if not message.text.isnumeric():
                return await message.answer("❌ Не верный тип данных, попробуйте еще раз")

            person = await Person.obj(user_id, session)
            person.balance_buffer_bank = person.balance_buffer_bank + int(message.text)
            await session.commit()
            await message.bot.send_message(user_id, f"✅ Ваш баланс копилки пополнен на +{message.text} AS командой ASTERI CLUB")
            await message.answer(f"✅ Баланс копилки {person.first_name} пополнен на +{message.text} AS")
            await state.finish()
            await admin_panel_user(message, str(user_id), session)
    else:
        await message.answer("❌ Не верный тип данных, попробуйте еще раз")


async def user_panel_bank_balance_minus(message: types.Message, user_id: int, state: FSMContext):

    await message.edit_text("✏ Введите число на сколько вы хотите уменьшить баланс копилки\nНажмите /CANCEL для отмены")
    await state.update_data(user_id=user_id)
    await state.set_state("user_panel_bank_minus_commit")


@session_db
async def user_panel_bank_minus_commit(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.content_type == "text":

        data = await state.get_data()
        user_id = int(data['user_id'])

        if message.text == "/CANCEL":
            await message.answer("🚫 Отмена", reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
            await admin_panel_user(message, str(user_id), session)
        else:
            if not message.text.isnumeric():
                return await message.answer("❌ Не верный тип данных, попробуйте еще раз")

            person = await Person.obj(user_id, session)
            money = int(message.text)

            person.balance_buffer_bank = person.balance_buffer_bank - money
            if person.balance_buffer_bank < 0:
                person.balance_bank = person.balance_bank + person.balance_buffer_bank
                person.balance_buffer_bank = 0

            await session.commit()

            await message.bot.send_message(user_id, f"♦ Ваш баланс копилки уменьшен на {message.text} AS командой ASTERI CLUB")
            await message.answer(f"♦ Баланс копилки {person.first_name} уменьшен на {message.text} AS")
            await state.finish()
            await admin_panel_user(message, str(user_id), session)
    else:
        await message.answer("❌ Не верный тип данных, попробуйте еще раз")


async def packet(message: types.Message, user_id: int, state: FSMContext, session: AsyncSession):
    await state.update_data(user_id=user_id)

    person = await Person.obj(user_id, session)

    packets_list = list(packets.keys())
    packets_list[packets_list.index(person.packet)] = person.packet + " ✅"

    text = "Выберите пакет, который хотите установить пользователю"
    markup = UserPanel.set_packet(user_id, packets_list)

    await message.edit_text(text, reply_markup=markup)


async def set_packet(message: types.Message, user_id: int, packet_name: str, state: FSMContext, session: AsyncSession):

    person = await Person.obj(user_id, session)

    person.packet = packet_name

    if packet_name != "FREE":
        await by_packet_view(user_id, packet_name)
        await update_title(person, session)

    await session.commit()

    await packet(message, user_id, state, session)




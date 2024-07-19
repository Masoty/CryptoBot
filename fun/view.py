import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.admin import ChatAdmin
from create_bot import bot
from data.config import packets, AS, admin_chat, chats_packets_url
from data.texts import *
from db.models import Person, Events
from buttons import *
from until import get_text_wallet, get_text_packet_panel, get_text_full_pay_usdt, get_partner_program_text, \
    minus_balance, update_title, update_refers_hierarchy, get_bank_text, get_text_full_pay_rub, \
    update_all_refers_hierarchy
from until import create_payment, kasa_check


async def about_bot(message: types.Message):
    markup = Button.about_bot()

    await message.answer(about_bot_text, reply_markup=markup)


async def send_number(message: types.Message, state: FSMContext, session: AsyncSession):
    # Если пользователь уже зарегистрировался, то функция не действительна
    person = await Person.obj(message.chat.id, session)
    if person.phone:
        return

    markup = Button.send_number()

    await message.answer(send_number_text, reply_markup=markup)
    await state.set_state("write_number")


async def user_agreement(message: types.Message):
    markup = Button.user_agreement()

    await message.answer(user_agreement_text, reply_markup=markup, parse_mode="HTML")

async def edit_city(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer(about_your_country_text, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state("edit_city_commit")

async def about_your_country(message: types.Message, state: FSMContext, session: AsyncSession):
    # Если пользователь уже зарегистрировался, то функция не действительна
    person = await Person.obj(message.chat.id, session)
    if person.city:
        return

    await message.answer(about_your_country_text, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state("about_your_country_commit")


async def hello(message: types.Message):

    await message.answer_photo(photo=types.InputFile("data/photo/hello.jpg"),
                               caption=hello_text.format(message.from_user.first_name),
                               parse_mode="HTML")
    await menu(message)


async def menu(message: types.Message, edit=False):
    await delete_keyboard(message)
    markup = Button.menu()

    if edit:
        await message.edit_media(types.InputMediaPhoto(types.InputFile("data/photo/menu.jpg")), reply_markup=markup)
    else:
        await message.answer_photo(photo=types.InputFile("data/photo/menu.jpg"), reply_markup=markup)


"""
                                        <<<   W A L L E T   >>>
"""


async def wallet(message: types.Message, session: AsyncSession):
    await delete_keyboard(message)
    text = await get_text_wallet(message, session)
    markup = await Button.get_markup_wallet(message, session)

    await message.edit_media(types.InputMediaPhoto(types.InputFile("data/photo/wallet.jpg"), text), reply_markup=markup)


async def by_packet(message: types.Message, session: AsyncSession):
    text = by_packet_text
    markup = await Button.by_packet(message, session)

    await message.edit_media(types.InputMediaPhoto(types.InputFile("data/photo/AS_packet.jpg"), text), reply_markup=markup)


async def by_packet_panel(message: types.Message, packet: str, session: AsyncSession):
    text = await get_text_packet_panel(message, packet, session)
    markup = await Button.by_packet_panel(packet)

    await message.edit_media(types.InputMediaPhoto(types.InputFile(f"data/photo/{packet}.jpg"), text),
                             reply_markup=markup)


async def full_pay_usdt(message: types.Message, packet: str, session: AsyncSession):
    text = await get_text_full_pay_usdt(message, packet, session)
    markup = await Button.full_pay_usdt(packet)

    await message.edit_media(types.InputMediaPhoto(types.InputFile(f"data/photo/{packet}.jpg"), text),
                             reply_markup=markup)

async def full_pay_rub(message: types.Message, packet: str, session: AsyncSession):

    text, price = await get_text_full_pay_rub(message, packet, session)
    payment_url, payment_id = await create_payment(price, f"Покупка {packet} пакета")
    markup = await Button.full_pay_rub(packet, url=payment_url)

    asyncio.create_task(kasa_check(message, payment_id, packet))

    await message.edit_media(types.InputMediaPhoto(types.InputFile(f"data/photo/{packet}.jpg"), text),
                             reply_markup=markup)


async def confirm_by_packet(message: types.Message, packet: str, session: AsyncSession):
    person = await Person.obj(message.chat.id, session=session)

    # Если баланс больше указанной суммы за пакет, то подключаем подписку
    # Вычетаем еще стоимость прошлых пакетов, если пользователь их купил
    if person.balance >= packets[packet] - packets[person.packet]:
        sum_minus = packets[packet] - packets[person.packet]
        await minus_balance(message, sum_minus, session)

        # Подтверждаем покупку пакета
        person.packet = packet
        await session.commit()

        await update_title(person, session)

        text = confirm_by_packet_success_text.format(packet, chats_packets_url[packet])

        await message.edit_media(
            types.InputMediaPhoto(types.InputFile(f"data/photo/{packet}.jpg"), text, parse_mode="HTML"))
        await menu(message)

    else:
        text = confirm_by_packet_error_text
        markup = await Button.confirm_by_packet_error()
        await message.edit_media(types.InputMediaPhoto(types.InputFile(f"data/photo/error.jpg"), text),
                                 reply_markup=markup)

async def by_packet_view(user_id: int, packet: str):
    text = confirm_by_packet_success_text.format(packet, chats_packets_url[packet])

    await bot.send_photo(user_id, photo=types.InputFile(f"data/photo/{packet}.jpg"), caption=text, parse_mode="HTML")


async def installment_rub(message: types.Message, packet: str, session: AsyncSession):
    text = installment_rub_text.format(AS)
    markup = await Button.installment_rub(message, packet, session)

    await message.edit_media(types.InputMediaPhoto(types.InputFile(f"data/photo/installment.jpg"), text),
                             reply_markup=markup)


async def delete_keyboard(message: types.Message, confid=False):
    try:
        if "Назад" in message.text or "Отмена" in message.text:
            message = await message.answer("Проверка...", reply_markup=types.ReplyKeyboardRemove())
            await message.delete()
        if confid:
            message = await message.answer("Проверка...", reply_markup=types.ReplyKeyboardRemove())
            await message.delete()
    except:
        pass


async def write_add_money(message: types.Message, state: FSMContext):
    await message.delete()

    await message.answer(write_add_money_text)
    await state.set_state("add_money_commit")


async def write_leave_money(message: types.Message, state: FSMContext):
    await message.delete()

    await message.answer(write_leave_money_text)
    await state.set_state("leave_money_commit")


async def write_wallet(message: types.Message, state: FSMContext):
    markup = Button.write_wallet()

    await message.answer(write_wallet_text, reply_markup=markup)
    await state.set_state("write_wallet_commit")


async def leave_money_true(message: types.Message, money: int, wallet_address: str, session: AsyncSession):
    await delete_keyboard(message, True)
    text = leave_money_true_text
    markup = Button.leave_money_true()

    await message.answer_photo(photo=types.InputFile(f"data/photo/application_commit.jpg"), caption=text,
                               reply_markup=markup)

    person = await Person.obj(message.chat.id, session)

    text = f"""
📤 Заявка на вывод средств

UserId: {person.user_id}
Имя: {person.first_name}
Username: @{person.username}
Сума: {money} AS
Адрес: {wallet_address}

    """
    markup = ChatAdmin.leave_money_balance(message.chat.id, money)

    await message.bot.send_message(admin_chat, text=text, reply_markup=markup)


async def leave_money_not_balance(message: types.Message):
    text = leave_money_not_balance_text
    markup = Button.leave_money_not_balance()

    await message.answer_photo(photo=types.InputFile(f"data/photo/not_money_on_balance.jpg"), caption=text,
                               reply_markup=markup)


"""
                                <<<  I N F O R M A T I O N   >>>
"""


async def information(message: types.Message, edit=True):
    text = information_text
    markup = Button.information()

    if edit:
        await message.edit_media(types.InputMediaPhoto(types.InputFile(f"data/photo/information.jpg"), text),
                                 reply_markup=markup)
    else:
        await message.answer_photo(photo=types.InputFile(f"data/photo/information.jpg"), caption=text,
                                   reply_markup=markup)


async def presentation(message: types.Message):
    text = presentation_text
    markup = Button.presentation()

    await message.edit_media(
        types.InputMediaPhoto(types.InputFile(f"data/photo/presentation.jpg"), text, parse_mode="HTML"),
        reply_markup=markup)


async def urls_chats(message: types.Message):
    text = urls_chats_text
    markup = Button.urls_chats()

    await message.edit_media(
        types.InputMediaPhoto(types.InputFile(f"data/photo/social_network.jpg"), text, parse_mode="HTML"),
        reply_markup=markup)


async def advance(message: types.Message):
    text = advance_text
    markup = Button.advance()

    await message.edit_media(
        types.InputMediaPhoto(types.InputFile(f"data/photo/advance.jpg"), text, parse_mode="HTML"),
        reply_markup=markup)


async def partner_program(message: types.Message, session: AsyncSession):
    text = await get_partner_program_text(message, session)
    markup = Button.partner_program()

    await message.edit_media(
        types.InputMediaPhoto(types.InputFile(f"data/photo/partner.jpg"), text, parse_mode="HTML"),
        reply_markup=markup)


"""
                                            <<<  B A N K   >>>
"""


async def bank(message: types.Message, session: AsyncSession, edit=True):
    text = await get_bank_text(message, session)
    markup = Button.bank()

    if edit:
        await message.edit_media(
            types.InputMediaPhoto(types.InputFile(f"data/photo/bank.jpg"), text, parse_mode="HTML"),
            reply_markup=markup)
    else:
        await message.answer_photo(photo=types.InputFile(f"data/photo/bank.jpg"), caption=text, parse_mode="HTML",
                                   reply_markup=markup)


async def add_bank(message: types.Message, state: FSMContext):
    await message.delete()

    text = bank_add_text
    markup = Button.add_bank()

    await message.answer(text, reply_markup=markup)
    await state.set_state("add_bank_check")


async def bank_add_true(message: types.Message, money: int):
    text = bank_add_true_text.format(money)
    markup = Button.bank_add_true(money)

    await message.answer(text, reply_markup=markup)


async def bank_add_commit(message: types.Message, money: int, session: AsyncSession):
    person = await Person.obj(message.chat.id, session)
    person.balance = person.balance - money
    person.balance_buffer_bank = person.balance_buffer_bank + money
    await session.commit()

    text = bank_add_commit_text.format(money)
    markup = Button.bank_add_commit()

    await message.edit_text(text=text, reply_markup=markup)


async def add_bank_not_balance(message: types.Message):
    text = add_bank_not_balance_text
    markup = Button.add_bank_not_balance()

    await message.answer(text, reply_markup=markup)


async def add_bank_incorrect(message: types.Message):
    text = add_bank_incorrect_text
    markup = Button.add_bank()

    await message.answer(text, reply_markup=markup)


async def leave_bank(message: types.Message, state: FSMContext):
    await message.delete()

    text = leave_bank_text
    markup = Button.add_bank()

    await message.answer(text, reply_markup=markup)
    await state.set_state("leave_bank_check")


async def bank_leave_true(message: types.Message, money: int):
    text = bank_leave_true_text.format(money)
    markup = Button.bank_leave_true(money)

    await message.answer(text, reply_markup=markup)


async def bank_leave_commit(message: types.Message, money: int, session: AsyncSession):
    person = await Person.obj(message.chat.id, session)

    if person.balance_bank + person.balance_buffer_bank >= money:
        # Система подщета баланса банка при выводе из нее денег
        person.balance_buffer_bank = person.balance_buffer_bank - money
        if person.balance_buffer_bank < 0:
            person.balance_bank = person.balance_bank + person.balance_buffer_bank
            person.balance_buffer_bank = 0

        await session.commit()

    text = f"""
💰 Заявка на вывод средств из копилки

UserId: {person.user_id}
Имя: {person.first_name}
Username: @{person.username}
Сума: {money} AS
    """
    markup = ChatAdmin.leave_money_balance_bank(message.chat.id, money)

    # Отправляем запрос в админ чат
    await message.bot.send_message(admin_chat, text, reply_markup=markup)

    text = bank_leave_commit_text.format(money)
    markup = Button.bank_add_commit()

    await message.edit_text(text=text, reply_markup=markup)


async def leave_bank_not_balance(message: types.Message):
    text = leave_bank_not_balance_text
    markup = Button.leave_bank_not_balance()

    await message.answer(text, reply_markup=markup)


async def leave_bank_incorrect(message: types.Message):
    text = leave_bank_incorrect_text
    markup = Button.add_bank()

    await message.answer(text, reply_markup=markup)

"""
                                                <<<  E V E N T S  >>>
"""


async def events(message: types.Message, session: AsyncSession):
    text = events_text
    markup = await Button.events(session)

    await message.edit_media(
        types.InputMediaPhoto(types.InputFile(f"data/photo/events.jpg"), text, parse_mode="HTML"), reply_markup=markup)


async def event_code(message: types.Message, event_id: int, session: AsyncSession):
    event = await Events.obj(event_id, session)

    if message.chat.id in event.users:
        is_sub = True
    else:
        is_sub = False

    text = event.text
    markup = await Button.event_code(event.price, is_sub, event_id)

    await message.edit_media(
        types.InputMediaPhoto(types.InputFile(f"data/events_photo/{event.event_id}.jpg"), text, parse_mode="HTML"),
        reply_markup=markup)


async def event_by(message: types.Message, event_id: int, session: AsyncSession):
    event = await Events.obj(event_id, session)

    if event.price == 0:
        text = event_free_by
    else:
        text = event_price_by.format(event.price)

    markup = await Button.event_by(event.price, event_id)

    await message.edit_media(
        types.InputMediaPhoto(types.InputFile(f"data/events_photo/{event.event_id}.jpg"), text, parse_mode="HTML"),
        reply_markup=markup)


async def event_commit(message: types.Message, event_id: int, session: AsyncSession):
    event = await Events.obj(event_id, session)
    person = await Person.obj(message.chat.id, session)

    if event.price != 0:
        if person.balance >= event.price:
            event.users.append(message.chat.id)
            l = event.users
            event.users = None
            await session.commit()

            event.users = l
            await session.commit()

            person.balance = person.balance - event.price
            await session.commit()

            await update_refers_hierarchy(person, event.price, session)
            await update_all_refers_hierarchy(person.refer, event.price, session)
            await update_title(person, session)
        else:
            text = "❌ Не достаточно средств"
            markup = Button.event_commit()
            return await message.edit_media(
                types.InputMediaPhoto(types.InputFile(f"data/events_photo/{event.event_id}.jpg"), text,
                                      parse_mode="HTML"), reply_markup=markup)
    else:
        event.users.append(message.chat.id)
        l = event.users
        event.users = None
        await session.commit()

        event.users = l
        await session.commit()

    text = event.text_success
    markup = Button.event_commit()

    await message.edit_media(
        types.InputMediaPhoto(types.InputFile(f"data/events_photo/{event.event_id}.jpg"), text, parse_mode="HTML"),
        reply_markup=markup)


async def event_view_success(message: types.Message, event_id: int, session: AsyncSession):
    event = await Events.obj(event_id, session)

    text = event.text_success
    markup = Button.event_commit()

    await message.edit_media(
        types.InputMediaPhoto(types.InputFile(f"data/events_photo/{event.event_id}.jpg"), text, parse_mode="HTML"),
        reply_markup=markup)

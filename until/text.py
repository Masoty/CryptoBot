from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import packets, AS
from data.texts import wallet_text, lite_by_plan, pro_by_plan, vip_by_plan, by_variant_packet_text, \
    partner_program_text, bank_text, get_text_full_pay_rub_text
from db.models import Person
from . import get_days_letters, get_bot_username, format_number


async def get_text_wallet(message: types.Message, session: AsyncSession):

    person = await Person.obj(message.chat.id, session)

    text = wallet_text.format(
        person.balance,
        person.balance_all_time,

        person.balance_bank + person.balance_buffer_bank,
        person.balance_all_time_bank,

        person.balance_all_time_partner,
        person.status,

        message.chat.id,
        f"{get_days_letters(person.data_register)} дней ({person.data_register})",
        person.packet,
        f"https://t.me/{await get_bot_username(message)}?start={message.chat.id}"
    )

    return text



async def get_text_packet_panel(message: types.Message, packet: str, session: AsyncSession):
    person = await Person.obj(message.chat.id, session)

    # Получаем стоимость текущего пакета
    # С вычетом текущей цены пакета
    price = packets[packet]-packets[person.packet]

    # Сколько в месяц в рублях нужно минимум платить
    installment_rub_mount = int((price * AS) / 10)

    if packet == "LITE":
        return lite_by_plan.format(price, format_number(installment_rub_mount))
    if packet == "PRO":
        return pro_by_plan.format(price, format_number(installment_rub_mount))
    if packet == "VIP":
        return vip_by_plan.format(price, format_number(installment_rub_mount))



async def get_text_full_pay_usdt(message: types.Message, packet: str, session: AsyncSession):

    person = await Person.obj(message.chat.id, session)

    # Получаем стоимость текущего пакета
    # Чтобы потом поучить стоимость следующего пакета
    price = packets[packet]-packets[person.packet]

    if packet == "LITE":
        return by_variant_packet_text.format(packet, price)
    if packet == "PRO":
        return by_variant_packet_text.format(packet, price)
    if packet == "VIP":
        return by_variant_packet_text.format(packet, price)


async def get_text_full_pay_rub(message: types.Message, packet: str, session: AsyncSession):

    person = await Person.obj(message.chat.id, session)

    # Получаем стоимость текущего пакета
    # Чтобы потом поучить стоимость следующего пакета
    price = packets[packet]-packets[person.packet]

    text = get_text_full_pay_rub_text.format(packet, price * AS)

    return text, price*AS

async def get_partner_program_text(message: types.Message, session: AsyncSession):
    person = await Person.obj(message.chat.id, session)
    refer = await Person.obj(person.refer, session)

    packets_level = {
        "FREE": "1 УРОВЕНЬ",
        "LITE": "2 УРОВНЯ",
        "PRO": "3 УРОВНЯ",
        "VIP": "5 УРОВНЕЙ"
    }

    text = partner_program_text.format(
        person.status,
        person.balance_all_time_partner,

        person.one_line_referrals,
        person.two_line_referrals,
        person.three_line_referrals,
        person.four_line_referrals,
        person.five_line_referrals,

        packets_level[person.packet],
        person.turnover_first_line,
        person.total_turnover,
        f'<a href="https://t.me/{refer.username}">{refer.first_name}</a>',
        f"https://t.me/{await get_bot_username(message)}?start={message.chat.id}"
    )

    return text


async def get_bank_text(message: types.Message, session: AsyncSession):
    person = await Person.obj(message.chat.id, session)

    text = bank_text.format(
        person.balance_bank,
        person.balance_buffer_bank,
        person.balance_all_time_bank
    )

    return text


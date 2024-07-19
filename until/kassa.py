import json

import asyncio
from aiogram import types
from aioyookassa.types.payment import PaymentAmount, Confirmation

from create_bot import bot
from data.config import YKASA_CLIENT, AS
from data.texts import confirm_by_packet_success_text
from db.models import Person
from until import add_packet_rub


async def create_payment(price: int, description: str):
    async with YKASA_CLIENT as client:
        confirmation = Confirmation(type='redirect', return_url='https://t.me/AsteriClubBot')
        payment = await client.create_payment(amount=PaymentAmount(value=price, currency='RUB'),
                                              description=description, confirmation=confirmation, capture=True)
        return payment.confirmation.url, payment.id


async def capture_payment(payment_id: str):
    async with YKASA_CLIENT as client:
        payment = await client.get_payment(payment_id)
        return json.loads(payment.json())


async def kasa_check(message: types.Message, payment_id: str, packet: str):
    for i in range(180):
        await asyncio.sleep(10)
        status = await capture_payment(payment_id)
        if status["status"] == "succeeded":
            await Person.set_packet(message.chat.id, packet)
            price = status["amount"]["value"] / AS
            await add_packet_rub(message.chat.id, int(price))
            try: await message.delete()
            except: pass
            text = confirm_by_packet_success_text.format(packet)

            await bot.send_photo(message.chat.id, photo=types.InputFile(f"data/photo/{packet}.jpg"), caption=text,
                                 parse_mode="HTML")
            return

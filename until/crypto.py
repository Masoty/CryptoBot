import asyncio
import httpx

from create_bot import bot
from data.config import API_KEY_PAYMENTS, TOKEN_AUTHORIZATION, EMAIL_CRYPTO, PASSWORD_CRYPTO
from db.models import Person


async def create_invoice(money: int, description: str):
    url = 'https://api.nowpayments.io/v1/invoice'
    headers = {
        'x-api-key': API_KEY_PAYMENTS,
        'Content-Type': 'application/json'
    }
    data = {
        "price_amount": money,
        "price_currency": "USDTTRC20",
        "order_description": description,
        "success_url": "https://t.me/AsteriClubBot",
        "cancel_url": "https://t.me/AsteriClubBot"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)

    invoice = response.json()
    return {"id": invoice["id"], "url": invoice["invoice_url"]}


async def get_list_payments(invoiceId: int):
    url = f'https://api.nowpayments.io/v1/payment/?invoiceId={invoiceId}'
    headers = {
        "Authorization": f"Bearer {TOKEN_AUTHORIZATION}",
        'x-api-key': API_KEY_PAYMENTS
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        res_json = response.json()

    return res_json

async def authorization():
    url = f'https://api.nowpayments.io/v1/auth'
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "email": EMAIL_CRYPTO,
        "password": PASSWORD_CRYPTO
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)
        res_json = response.json()

    return res_json


async def check_user_pay(user_id: int, price: int, invoice_id: int):

    for i in range(180):
        await asyncio.sleep(10)

        try:
            res_check = await get_list_payments(invoice_id)
            for res in res_check["data"]:
                if res["payment_status"] == "finished":
                    print("Баланс пополнен")

                    await Person.add_balance(user_id, price)

                    await bot.send_message(user_id, f"✅ Ваш баланс пополнен на {price} AS")
                    return
        except Exception as e:
            if "data" in str(e):
                break

            print(e)

    await bot.send_message(user_id,
                           f"❌ Ваш запрос на пополнение {price} AS истек, ссылка на оплату больше не действительна")
    return


async def updates_token():

    while True:
        try:
            token = await authorization()
            TOKEN_AUTHORIZATION = token["token"]
        except Exception as e:
            print(e)
            pass

        await asyncio.sleep(200)



import asyncio
from aiogram.utils import executor

from create_bot import dp

from db.db import global_init
from db.models import Person
from until import bank_updates_every_week
from handlers.register_handlers import return_handlers
from until.crypto import updates_token

return_handlers(dp)

async def init_bot(_):
    await global_init()
    await Person.register_ziro_acc()
    asyncio.create_task(bank_updates_every_week())
    asyncio.create_task(updates_token())
    print("Токен обновлен")
    print("🔥🔥🔥 Bot Started 🔥🔥🔥")

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=init_bot)


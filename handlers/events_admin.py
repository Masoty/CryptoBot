from aiogram import types
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import session_db
from db.models import Events
from until.events import event_add, events


@session_db
async def events_handler(callback: types.CallbackQuery, callback_data: dict, state: FSMContext, session: AsyncSession):
    action = callback_data['action']
    message = callback.message
    await callback.answer()
    if action == "add":
        await event_add(message, state)
    if action == "delete":
        await Events.delete(int(callback_data['event_id']), session)
        await events(message, edit=True)






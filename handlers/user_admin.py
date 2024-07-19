from until.user_admin import *

from aiogram import types
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import session_db
from until.chat_admin import leave_balance_true, leave_balance_false, leave_balance_bank_true, leave_balance_bank_false


@session_db
async def user_admin_handler(callback: types.CallbackQuery, callback_data: dict, state: FSMContext, session: AsyncSession):
    action = callback_data['action']
    user_id = int(callback_data['user_id'])
    message = callback.message
    await callback.answer()
    if action == "balance_add":
        await user_panel_add(message, user_id, state)
    if action == "balance_minus":
        await user_panel_minus(message, user_id, state)
    if action == "balance_bank_add":
        await user_panel_bank_balance_add(message, user_id, state)
    if action == "balance_bank_minus":
        await user_panel_bank_balance_minus(message, user_id, state)
    if action == "packet":
        await packet(message, user_id, state, session)
    if action == "menu":
        await admin_panel_user(message, str(user_id), session, edit=True)
    if "set_packet_" in action:
        await set_packet(message, user_id, action.replace("set_packet_", ""), state, session)


@session_db
async def admin_chat(callback: types.CallbackQuery, callback_data: dict, state: FSMContext, session: AsyncSession):
    action = callback_data['action']
    user_id = int(callback_data['user_id'])
    money = int(callback_data['money'])
    message = callback.message
    await callback.answer()
    if action == "leave_balance_true":
        await leave_balance_true(message, user_id, money)
    if action == "leave_balance_false":
        await leave_balance_false(message, user_id, money, session)
    if action == "leave_balance_bank_true":
        await leave_balance_bank_true(message, user_id, money, session)
    if action == "leave_balance_bank_false":
        await leave_balance_bank_false(message, user_id, money, session)





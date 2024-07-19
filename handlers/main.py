from fun.view import *
from db.db import session_db
from until.chat_admin import edit_procent
from until.user_admin import admin_panel_user


@session_db
async def data(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):

    if call.data == "wallet":
        await wallet(call.message, session)
    if call.data == "by_packet":
        await by_packet(call.message, session)
    if "by_packet__" in call.data:
        await by_packet_panel(call.message, call.data.replace("by_packet__", ""), session)
    if "full_pay_usdt_" in call.data:
        await full_pay_usdt(call.message, call.data.replace("full_pay_usdt_", ""), session)
    if "full_pay_rub_" in call.data:
        await full_pay_rub(call.message, call.data.replace("full_pay_rub_", ""), session)
    if "confirm_by_packet_" in call.data:
        await confirm_by_packet(call.message, call.data.replace("confirm_by_packet_", ""), session)
    if "installment_rub_" in call.data:
        await installment_rub(call.message, call.data.replace("installment_rub_", ""), session)
    if "wallet_add_money" == call.data:
        await write_add_money(call.message, state)
    if "leave_money" == call.data:
        await write_leave_money(call.message, state)

    if "information" == call.data:
        await information(call.message)
    if "presentation" == call.data:
        await presentation(call.message)
    if "urls_chats" == call.data:
        await urls_chats(call.message)
    if "advance" == call.data:
        await advance(call.message)
    if "edit_city" == call.data:
        await edit_city(call.message, state)

    if "partner_program" == call.data:
        await partner_program(call.message, session)

    if "bank" == call.data:
        await bank(call.message, session=session)

    if call.data == "menu":
        await menu(call.message, edit=True)
    if call.data == "menu_bank":
        await call.message.delete()
        await menu(call.message, edit=False)
    if call.data == "add_bank":
        await add_bank(call.message, state)
    if "bank_add_commit_" in call.data:
        money = int(call.data.replace("bank_add_commit_", ""))
        await bank_add_commit(call.message, money, session)
    if "bank_not_edit" == call.data:
        try: await call.message.delete()
        except: pass
        await call.message.answer(text="🚫 Отменено", reply_markup=types.ReplyKeyboardRemove())
        await bank(call.message, edit=False, session=session)

    if "bank_leave_commit_" in call.data:
        money = int(call.data.replace("bank_leave_commit_", ""))
        await bank_leave_commit(call.message, money, session)
    if "leave_bank" == call.data:
        await leave_bank(call.message, state)

    if "events" == call.data:
        await events(call.message, session)
    if "event_code_" in call.data:
        event_id = int(call.data.replace("event_code_", ""))
        await event_code(call.message, event_id, session)
    if "event_by_" in call.data:
        event_id = int(call.data.replace("event_by_", ""))
        await event_by(call.message, event_id, session)
    if "event_commit_" in call.data:
        event_id = int(call.data.replace("event_commit_", ""))
        await event_commit(call.message, event_id, session)
    if "event_view_success_" in call.data:
        event_id = int(call.data.replace("event_view_success_", ""))
        await event_view_success(call.message, event_id, session)

    if "edit_procent" == call.data:
        await edit_procent(call.message, state)

@session_db
async def text_handler(message, state: FSMContext, session: AsyncSession):

    if message.text == "Начать ✅":
        await send_number(message, state, session)
    if message.text == "✅ Принимаю":
        await about_your_country(message, state, session)
    if "user_" in message.text:
        await admin_panel_user(message, message.text.replace("user_", ""), session)
    if "Назад" in message.text or "Отмена" in message.text:
        await delete_keyboard(message)

from aiogram import Dispatcher

from buttons.admin import events_cb_data, user_panel_cb_data, chat_admin_cb_data
from handlers.edit import *
from handlers.events_admin import events_handler
from handlers.main import text_handler, data
from handlers.other import start
from handlers.user_admin import user_admin_handler, admin_chat
from until.chat_admin import get_all_users, procent, edit_procent_commit, get_events_users, send_all_users, \
    send_all_users_commit
from until.events import events, event_write_title, events_write_text, event_write_price, event_write_photo, \
    event_write_success
from until.user_admin import user_panel_add_commit, user_panel_minus_commit, user_panel_bank_minus_commit, \
    user_panel_bank_add_commit


def return_handlers(dp: Dispatcher):

    dp.register_message_handler(start, commands=["start"])

    # Events Admin
    dp.register_message_handler(events, commands=["events"])
    dp.register_message_handler(get_all_users, commands=["get_all_users"])
    dp.register_message_handler(procent, commands=["procent"])
    dp.register_message_handler(get_events_users, commands=["get_events_users"])
    dp.register_message_handler(send_all_users, commands=["send_all_users"])
    dp.register_callback_query_handler(events_handler, events_cb_data.filter())

    # user panel
    dp.register_callback_query_handler(user_admin_handler, user_panel_cb_data.filter())
    dp.register_callback_query_handler(admin_chat, chat_admin_cb_data.filter())

    dp.register_message_handler(text_handler, content_types=["text"])
    dp.register_callback_query_handler(data, lambda call: call.data)

    dp.register_message_handler(write_number, state="write_number", content_types=types.ContentTypes.ANY)
    dp.register_message_handler(about_your_country_commit, state="about_your_country_commit", content_types=types.ContentTypes.ANY)
    dp.register_message_handler(edit_city_commit, state="edit_city_commit", content_types=types.ContentTypes.ANY)

    dp.register_message_handler(leave_money_commit, state="leave_money_commit", content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(add_money_commit, state="add_money_commit", content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(write_wallet_commit, state="write_wallet_commit", content_types=types.ContentTypes.TEXT)

    dp.register_message_handler(add_bank_check, state="add_bank_check", content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(leave_bank_check, state="leave_bank_check", content_types=types.ContentTypes.TEXT)

    dp.register_message_handler(event_write_title, state="event_write_title", content_types=types.ContentTypes.ANY)
    dp.register_message_handler(event_write_photo, state="event_write_photo", content_types=types.ContentTypes.ANY)
    dp.register_message_handler(events_write_text, state="events_write_text", content_types=types.ContentTypes.ANY)
    dp.register_message_handler(event_write_success, state="event_write_success", content_types=types.ContentTypes.ANY)
    dp.register_message_handler(event_write_price, state="event_write_price", content_types=types.ContentTypes.ANY)

    dp.register_message_handler(user_panel_add_commit, state="user_panel_add_commit", content_types=types.ContentTypes.ANY)
    dp.register_message_handler(user_panel_minus_commit, state="user_panel_minus_commit", content_types=types.ContentTypes.ANY)
    dp.register_message_handler(user_panel_bank_add_commit, state="user_panel_bank_add_commit", content_types=types.ContentTypes.ANY)
    dp.register_message_handler(user_panel_bank_minus_commit, state="user_panel_bank_minus_commit", content_types=types.ContentTypes.ANY)

    dp.register_message_handler(edit_procent_commit, state="edit_procent_commit", content_types=types.ContentTypes.ANY)
    dp.register_message_handler(send_all_users_commit, state="send_all_users_commit", content_types=types.ContentTypes.ANY)







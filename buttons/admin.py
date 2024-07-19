
from aiogram import types
from aiogram.utils.callback_data import CallbackData
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Events

events_cb_data = CallbackData("events_admin", "action", "event_id")
user_panel_cb_data = CallbackData("user_panel", "action", "user_id")
chat_admin_cb_data = CallbackData("chat_admin", "action", "user_id", "money")

class AdminButtons:

    @staticmethod
    async def events(session: AsyncSession):
        markup = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)

        list_buttons = await Events.get_events(session)

        for event in list_buttons:
            markup.add(types.InlineKeyboardButton(event.name, callback_data="/"), types.InlineKeyboardButton("❌", callback_data=events_cb_data.new(action="delete", event_id=int(event.event_id))))

        b2 = types.InlineKeyboardButton("➕ Добавить Мероприятие", callback_data=events_cb_data.new(action="add", event_id=0))
        markup.add(b2)
        return markup

    @staticmethod
    def close():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        b1 = types.KeyboardButton("🚫 Отмена")
        markup.add(b1)
        return markup

    @staticmethod
    def procent():
        markup = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
        b1 = types.InlineKeyboardButton("✏ Изменить процент", callback_data="edit_procent")
        markup.add(b1)
        return markup



class UserPanel:

    @staticmethod
    def panel(user_id: int):
        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        b1 = types.InlineKeyboardButton("Увеличить баланс", callback_data=user_panel_cb_data.new(action="balance_add", user_id=user_id))
        b2 = types.InlineKeyboardButton("Уменьшить баланс", callback_data=user_panel_cb_data.new(action="balance_minus", user_id=user_id))
        b3 = types.InlineKeyboardButton("Увеличить копилку", callback_data=user_panel_cb_data.new(action="balance_bank_add", user_id=user_id))
        b4 = types.InlineKeyboardButton("Уменьшить копилку", callback_data=user_panel_cb_data.new(action="balance_bank_minus", user_id=user_id))
        b5 = types.InlineKeyboardButton("Установить пакет", callback_data=user_panel_cb_data.new(action="packet", user_id=user_id))
        markup.add(b1, b2, b3, b4, b5)
        return markup

    @staticmethod
    def set_packet(user_id: int, text: list):
        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        b1 = types.InlineKeyboardButton(text[0], callback_data=user_panel_cb_data.new(action="set_packet_FREE", user_id=user_id))
        b2 = types.InlineKeyboardButton(text[1], callback_data=user_panel_cb_data.new(action="set_packet_LITE", user_id=user_id))
        b3 = types.InlineKeyboardButton(text[2], callback_data=user_panel_cb_data.new(action="set_packet_PRO", user_id=user_id))
        b4 = types.InlineKeyboardButton(text[3], callback_data=user_panel_cb_data.new(action="set_packet_VIP", user_id=user_id))
        b5 = types.InlineKeyboardButton("⬅ Назад", callback_data=user_panel_cb_data.new(action="menu", user_id=user_id))
        markup.add(b1, b2, b3, b4, b5)
        return markup


class ChatAdmin:

    @staticmethod
    def leave_money_balance(user_id: int, money: int):
        markup = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
        b1 = types.InlineKeyboardButton("✅ Вывод завершен", callback_data=chat_admin_cb_data.new(action="leave_balance_true", user_id=user_id, money=money))
        b2 = types.InlineKeyboardButton("❌ Отменить вывод", callback_data=chat_admin_cb_data.new(action="leave_balance_false", user_id=user_id, money=money))
        markup.add(b1, b2)
        return markup

    @staticmethod
    def leave_money_balance_bank(user_id: int, money: int):
        markup = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
        b1 = types.InlineKeyboardButton("✅ Вывод завершен", callback_data=chat_admin_cb_data.new(action="leave_balance_bank_true", user_id=user_id, money=money))
        b2 = types.InlineKeyboardButton("❌ Отменить вывод", callback_data=chat_admin_cb_data.new(action="leave_balance_bank_false", user_id=user_id, money=money))
        markup.add(b1, b2)
        return markup







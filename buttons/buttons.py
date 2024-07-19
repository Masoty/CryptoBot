from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import packets, AS, installment_plan
from db.models import Person, Events
from until import format_number

class Button:


    @staticmethod
    def about_bot():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        b1 = types.KeyboardButton("Начать ✅")
        markup.add(b1)
        return markup

    @staticmethod
    def send_number():
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        b1 = types.KeyboardButton("📤 Отправить номер телефона", request_contact=True)
        markup.add(b1)
        return markup

    @staticmethod
    def user_agreement():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        b1 = types.KeyboardButton("✅ Принимаю")
        markup.add(b1)
        return markup

    @staticmethod
    def menu():
        markup = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
        b1 = types.InlineKeyboardButton("Кошелек 💼", callback_data="wallet")
        b2 = types.InlineKeyboardButton("Копилка 💰", callback_data="bank")
        b3 = types.InlineKeyboardButton("Партнерка ⚖", callback_data="partner_program")
        b4 = types.InlineKeyboardButton("Мероприятия 🎟", callback_data="events")
        b5 = types.InlineKeyboardButton("Информация ℹ", callback_data="information")
        b6 = types.InlineKeyboardButton("Поддержка ⚙", url="https://t.me/AsteriSupport")
        markup.add(b1, b2, b3, b4, b5, b6)
        return markup

    @staticmethod
    async def get_markup_wallet(message: types.Message, session: AsyncSession):

        person = await Person.obj(message.chat.id, session)

        if person.packet == "FREE":
            b1 = types.InlineKeyboardButton("📘 Приобрести AS-пакет", callback_data="by_packet")
        elif person.packet == "LITE":
            b1 = types.InlineKeyboardButton("📘 АПГРЕЙД", callback_data="by_packet")
        elif person.packet == "PRO":
            b1 = types.InlineKeyboardButton("📘 АПГРЕЙД", callback_data="by_packet")
        else:
            b1 = types.InlineKeyboardButton("ЛИЧНОЕ НАСТАВНИЧЕСТВО", url="https://forms.yandex.ru/u/64f79e2cd046884dedf64a91")

        b2 = types.InlineKeyboardButton("📥 Пополнить", callback_data="wallet_add_money")
        b3 = types.InlineKeyboardButton("📤 Вывести", callback_data="leave_money")
        b4 = types.InlineKeyboardButton("⬅ Назад", callback_data="menu")

        markup = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add(b1); markup.add(b2, b3); markup.add(b4)
        return markup

    @staticmethod
    async def by_packet(message: types.Message, session: AsyncSession):

        person = await Person.obj(message.chat.id, session)

        packet = ["FREE", "LITE", "PRO", "VIP"]

        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)

        for pc_name in packet[packet.index(person.packet)+1:]:
            markup.add(types.InlineKeyboardButton(f'ПАКЕТ "ASTERI {pc_name}"', callback_data=f"by_packet__{pc_name}"))

        markup.add(types.InlineKeyboardButton('⬅ Назад', callback_data=f"wallet"))

        return markup

    @staticmethod
    async def by_packet_panel(packet: str):

        b1 = types.InlineKeyboardButton("ПОЛНАЯ ОПЛАТА В AS", callback_data=f"full_pay_usdt_{packet}")
        b2 = types.InlineKeyboardButton("ПОЛНАЯ ОПЛАТА В RUB", callback_data=f"full_pay_rub_{packet}")
        b3 = types.InlineKeyboardButton("РАССРОЧКА В RUB", callback_data=f"installment_rub_{packet}")
        b4 = types.InlineKeyboardButton("⬅ Назад", callback_data="by_packet")

        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(b1, b2, b3, b4)
        return markup

    @staticmethod
    async def full_pay_usdt(packet: str):

        b1 = types.InlineKeyboardButton(f"✅ ПРИОБРЕСТИ ПАКЕТ “{packet}”", callback_data=f"confirm_by_packet_{packet}")
        b2 = types.InlineKeyboardButton("⬅ Назад", callback_data=f"by_packet__{packet}")

        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(b1, b2)
        return markup

    @staticmethod
    async def full_pay_rub(packet: str, url: str):

        b1 = types.InlineKeyboardButton(f"Перейти", url=url)
        b2 = types.InlineKeyboardButton("⬅ Назад", callback_data=f"by_packet__{packet}")

        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(b1, b2)
        return markup


    @staticmethod
    async def confirm_by_packet_success():
        b1 = types.InlineKeyboardButton(f"Главное меню 📲", callback_data=f"menu")

        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(b1)
        return markup


    @staticmethod
    async def confirm_by_packet_error():
        b1 = types.InlineKeyboardButton(f"📥 Пополнить", callback_data=f"wallet_add_money")
        b2 = types.InlineKeyboardButton(f"Главное меню 📲", callback_data=f"menu")

        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(b1, b2)
        return markup

    @staticmethod
    async def installment_rub(message: types.Message, packet: str, session: AsyncSession):

        person = await Person.obj(message.chat.id, session)

        all_sum = packets[packet] - packets[person.packet]

        list_urls = installment_plan[f"{person.packet}_{packet}"]

        b1 = types.InlineKeyboardButton(f"Платеж {format_number(int((all_sum*AS)/10))} руб/мес (10 месяцев)", url=list_urls[0])
        b2 = types.InlineKeyboardButton(f"Платеж {format_number(int((all_sum*AS)/6))} руб/мес (6 месяцев)", url=list_urls[1])
        b3 = types.InlineKeyboardButton(f"Платеж {format_number(int((all_sum*AS)/4))} руб/мес (4 месяцев)", url=list_urls[2])
        b4 = types.InlineKeyboardButton(f"Связаться с нами", url="https://t.me/AsteriSupport")
        b5 = types.InlineKeyboardButton(f"⬅ Назад", callback_data=f"by_packet__{packet}")

        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(b1, b2, b3, b4, b5)
        return markup


    @staticmethod
    async def add_money():
        b1 = types.InlineKeyboardButton(f"✏ Указать сумму вывода", callback_data=f"write_add_money")
        b2 = types.InlineKeyboardButton("⬅ Назад", callback_data=f"wallet")

        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(b1, b2)
        return markup

    @staticmethod
    async def add_money_commit(url: str):
        b1 = types.InlineKeyboardButton(f"Перейти", url=url)
        b2 = types.InlineKeyboardButton("Главное меню 📲", callback_data=f"menu")

        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(b1, b2)
        return markup

    @staticmethod
    async def leave_money():
        b1 = types.InlineKeyboardButton(f"✏ Указать сумму вывода", callback_data=f"write_leave_money")
        b2 = types.InlineKeyboardButton("⬅ Назад", callback_data=f"wallet")

        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(b1, b2)
        return markup

    @staticmethod
    def write_wallet():
        b1 = types.KeyboardButton("❌ Отмена")

        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        markup.add(b1)
        return markup

    @staticmethod
    def leave_money_true():
        b1 = types.InlineKeyboardButton(f"Главное меню 📲", callback_data=f"menu")

        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(b1)
        return markup


    @staticmethod
    def leave_money_not_balance():
        b1 = types.InlineKeyboardButton(f"Связаться с нами", url="https://t.me/AsteriSupport")
        b2 = types.InlineKeyboardButton("⬅ Назад", callback_data=f"wallet")

        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(b1, b2)
        return markup

    @staticmethod
    def information():

        b1 = types.InlineKeyboardButton(f"Презентация 👩🏽‍💻", callback_data=f"presentation")
        b2 = types.InlineKeyboardButton(f"Ссылки на чаты 💬", callback_data=f"urls_chats")
        b3 = types.InlineKeyboardButton(f"Продвижение 💸", callback_data=f"advance")
        b4 = types.InlineKeyboardButton(f"Изменить город", callback_data=f"edit_city")
        b5 = types.InlineKeyboardButton("Главное меню 📲", callback_data=f"menu")

        markup = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add(b1, b2); markup.add(b3, b4); markup.add(b5)
        return markup


    @staticmethod
    def presentation():

        b1 = types.InlineKeyboardButton(f"Скачать презентацию", url="https://disk.yandex.ru/d/8SzP6nQ2UODfRA")
        b2 = types.InlineKeyboardButton(f"Задать вопрос", url="https://t.me/AsteriSupport")
        b3 = types.InlineKeyboardButton("⬅ Назад", callback_data=f"information")

        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(b1, b2, b3)
        return markup

    @staticmethod
    def urls_chats():
        b1 = types.InlineKeyboardButton(f"Задать вопрос", url="https://t.me/AsteriSupport")
        b2 = types.InlineKeyboardButton("⬅ Назад", callback_data=f"information")

        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(b1, b2)
        return markup

    @staticmethod
    def advance():
        b1 = types.InlineKeyboardButton(f"Шаблоны для продвижения", url="https://disk.yandex.ru/d/8SzP6nQ2UODfRA")
        b2 = types.InlineKeyboardButton(f"Задать вопрос", url="https://t.me/AsteriSupport")
        b3 = types.InlineKeyboardButton("⬅ Назад", callback_data=f"information")

        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(b1, b2, b3)
        return markup

    @staticmethod
    def partner_program():
        b1 = types.InlineKeyboardButton(f"СКАЧАТЬ PDF-ПРЕЗЕНТАЦИЮ", url="https://disk.yandex.ru/d/8SzP6nQ2UODfRA")
        b2 = types.InlineKeyboardButton(f"ВИДЕО-ОБУЧЕНИЕ", url="https://www.youtube.com/playlist?list=PLu6vOyQnv6Vy65mcBdfiw85n88dSxkR-x")
        b3 = types.InlineKeyboardButton("Главное меню 📲", callback_data=f"menu")

        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(b1, b2, b3)
        return markup


    @staticmethod
    def bank():
        b1 = types.InlineKeyboardButton(f"📥 Пополнить", callback_data=f"add_bank")
        b2 = types.InlineKeyboardButton(f"📤 Вывести", callback_data=f"leave_bank")
        b3 = types.InlineKeyboardButton("Главное меню 📲", callback_data=f"menu")

        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(b1, b2, b3)
        return markup

    @staticmethod
    def add_bank():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        b1 = types.KeyboardButton("⬅ Назад")
        markup.add(b1)
        return markup

    @staticmethod
    def bank_add_true(number: int):
        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        b1 = types.InlineKeyboardButton("✅ ПОПОЛНИТЬ КОПИЛКУ", callback_data=f"bank_add_commit_{number}")
        b2 = types.InlineKeyboardButton("⬅ Назад", callback_data="bank_not_edit")
        markup.add(b1, b2)
        return markup

    @staticmethod
    def bank_add_commit():
        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        b1 = types.InlineKeyboardButton("Главное меню 📲", callback_data="menu_bank")
        markup.add(b1)
        return markup

    @staticmethod
    def add_bank_not_balance():
        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        b1 = types.InlineKeyboardButton(f"📥 Пополнить", callback_data=f"wallet_add_money")
        b2 = types.InlineKeyboardButton("⬅ Назад", callback_data="bank_not_edit")
        markup.add(b1, b2)
        return markup

    @staticmethod
    def bank_leave_true(number: int):
        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        b1 = types.InlineKeyboardButton("✅ Вывести AS из копилки", callback_data=f"bank_leave_commit_{number}")
        b2 = types.InlineKeyboardButton("⬅ Назад", callback_data="bank_not_edit")
        markup.add(b1, b2)
        return markup


    @staticmethod
    def leave_bank_not_balance():
        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        b1 = types.InlineKeyboardButton(f"Связаться с нами", url="https://t.me/AsteriSupport")
        b2 = types.InlineKeyboardButton("⬅ Назад", callback_data="bank_not_edit")
        markup.add(b1, b2)
        return markup

    @staticmethod
    async def events(session: AsyncSession):

        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)

        list_buttons = await Events.get_events(session)

        for event in list_buttons:
            markup.add(types.InlineKeyboardButton(event.name, callback_data=f"event_code_{event.event_id}"))

        b2 = types.InlineKeyboardButton("Главное меню 📲", callback_data="menu")
        markup.add(b2)
        return markup


    @staticmethod
    async def event_code(price: int, is_sub: bool, event_id: int):

        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)

        if is_sub:
            b1 = types.InlineKeyboardButton("✅ Вы уже записаны", callback_data=f"event_view_success_{event_id}")
        elif price == 0:
            b1 = types.InlineKeyboardButton("✅ Записаться", callback_data=f"event_by_{event_id}")
        else:
            b1 = types.InlineKeyboardButton("✅ Оплатить", callback_data=f"event_by_{event_id}")

        b2 = types.InlineKeyboardButton(f"Связаться с нами", url="https://t.me/AsteriSupport")
        b3 = types.InlineKeyboardButton("⬅ Назад", callback_data="events")
        markup.add(b1, b2, b3)
        return markup

    @staticmethod
    async def event_by(price: int, event_id: int):
        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)

        b1 = types.InlineKeyboardButton("✅ Да, верно", callback_data=f"event_commit_{event_id}")

        if price == 0:
            b2 = types.InlineKeyboardButton("❌ Отмена", callback_data=f"event_code_{event_id}")
        else:
            b2 = types.InlineKeyboardButton("⬅ Назад", callback_data=f"event_code_{event_id}")

        markup.add(b1, b2)
        return markup

    @staticmethod
    def event_commit():
        markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
        b1 = types.InlineKeyboardButton("Главное меню 📲", callback_data="menu")
        markup.add(b1)
        return markup




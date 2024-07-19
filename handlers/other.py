from aiogram import types
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from data.texts import text_registration
from db.db import session_db
from db.models import Person
from until import register_refers_line
from fun.view import about_bot, menu, send_number


@session_db
async def start(message: types.Message, state: FSMContext, session: AsyncSession):

    # Проверяем, если пользователь уже зарегистрировался то отправляем его сразу в меню
    is_register = await Person.is_register(message.chat.id, session)
    if is_register:
        return await menu(message)

    # Проверка есть ли реф ссылка
    if "/start " in message.text:

        # Получаем рефера
        refer_id = message.text.replace("/start ", "")

        # Проверяем id ли ето, а не рандомный какой-то текст
        if refer_id.isnumeric():

            # Проверяем существует ли рефер, или ето фейковый рефер
            is_refer = await Person.is_register(int(refer_id), session)

            # Если этот рефер существует
            if is_refer:
                is_register = await Person.is_register(message.chat.id, session)

                # Если этот пользователь уже зарегистрирован
                if is_register:
                    await menu(message)
                else:
                    # Если не зарегистрирован, регистрируем
                    await Person.register(user_id=message.chat.id, first_name=message.from_user.first_name, refer=int(refer_id), username=message.from_user.username, session=session)
                    await register_refers_line(message, session)
                    await send_number(message, state, session)
            else:
                await message.answer("⛔ Вы перешли по неверной реферальной ссылке, такого человека не существует в нашем проекте\nПопросите реферальную ссылку у человека, который рассказал вам про наше сообщество. Если такого человека нет, то свяжитесь с нами 👉 @ASTERISUPPORT")
        else:
            await message.answer(
                "⛔ Вы перешли по неверной реферальной ссылке, такого человека не существует в нашем проекте\nПопросите реферальную ссылку у человека, который рассказал вам про наше сообщество. Если такого человека нет, то свяжитесь с нами 👉 @ASTERISUPPORT")
    else:
        await message.answer("⛔ Доступ в бот возможен только по рекомендации от участников сообщества. Попросите реферальную ссылку у человека, который рассказал вам про наше сообщество. Если такого человека нет, то свяжитесь с нами 👉 @ASTERISUPPORT")





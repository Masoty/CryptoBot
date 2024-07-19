import os
import random

import aiofiles
from aiogram import types
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.admin import AdminButtons
from data.config import admins
from db.db import session_db
from db.models import Events


@session_db
async def events(message: types.Message, session: AsyncSession, edit=False):
    if message.chat.id in admins:
        text = "Админ панель Мероприятий"
        markup = await AdminButtons.events(session)

        if edit:
            await message.edit_text(text, parse_mode="HTML", reply_markup=markup)
        else:
            await message.answer(text, parse_mode="HTML", reply_markup=markup)


async def event_add(message: types.Message, state: FSMContext):
    markup = AdminButtons.close()
    await message.delete()
    await message.answer("✏ Введите название кнопки, пример - 1.09.23 Москва - Финансовое развитие",
                         reply_markup=markup)
    await state.update_data(event_id=random.randint(1, 999999))
    await state.set_state("event_write_title")


async def event_write_title(message: types.Message, state: FSMContext):
    if message.content_type == "text":
        if message.text == "🚫 Отмена":
            await message.answer("🚫 Отмена", reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
            await events(message)
        else:
            await message.answer("✏ Скиньте фото мероприятия")
            await state.update_data(title=message.text)
            await state.set_state("event_write_photo")
    else:
        await message.answer("❌ Не верный тип данных, попробуйте еще раз")


async def event_write_photo(message: types.Message, state: FSMContext):
    if message.content_type == "text":
        if message.text == "🚫 Отмена":
            await message.answer("🚫 Отмена", reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
            await events(message)
    elif message.content_type == "photo":
        photo = message.photo[-1]  # Получение последней (наибольшей) версии фотографии
        file_id = photo.file_id

        data = await state.get_data()

        file_path = f"data/events_photo/{data['event_id']}.jpg"  # Путь для сохранения фото

        # Скачивание файла по его file_id
        file = await message.bot.download_file_by_id(file_id)

        async with aiofiles.open(file_path, mode='wb') as f:
            await f.write(file.read())

        await message.answer("✏ Введите текст сообщения")
        await state.set_state("events_write_text")
    else:
        await message.answer("❌ Не верный тип данных, попробуйте еще раз")


async def events_write_text(message: types.Message, state: FSMContext):
    if message.content_type == "text":
        if message.text == "🚫 Отмена":
            await message.answer("🚫 Отмена", reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
            await events(message)
        else:

            if len(message.text) > 1024:
                return await message.answer("❌ Текст слишком длинный и занимает больше 1024 байт, попробуйте еще раз")

            await message.answer("✏ Введите цену за мероприятие, 0 - бесплатно")
            await state.update_data(text=message.text)
            await state.set_state("event_write_price")
    else:
        await message.answer("❌ Не верный тип данных, попробуйте еще раз")


async def event_write_price(message: types.Message, state: FSMContext):
    if message.content_type == "text":
        if message.text == "🚫 Отмена":
            await message.answer("🚫 Отмена", reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
            await events(message)
        else:
            if not message.text.isnumeric():
                return await message.answer("❌ Цену нужно вводить цифрами, попробуйте еще раз")

            await message.answer("✏ Введите сообщение после успешной покупки")
            await state.update_data(price=int(message.text))
            await state.set_state("event_write_success")
    else:
        await message.answer("❌ Не верный тип данных, попробуйте еще раз")


async def event_write_success(message: types.Message, state: FSMContext):
    if message.content_type == "text":
        if message.text == "🚫 Отмена":
            await message.answer("🚫 Отмена", reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
            await events(message)
        else:
            if len(message.text) > 1024:
                return await message.answer("❌ Текст слишком длинный и занимает больше 1024 байт, попробуйте еще раз")

            await state.update_data(text_success=message.text)
            await events_commit(message, state)
            await delete_events_photo()
    else:
        await message.answer("❌ Не верный тип данных, попробуйте еще раз")

@session_db
async def delete_events_photo(session: AsyncSession):

    """
    Удаляет фото мероприятий, которые уже не используются
    """

    all_events = await Events.get_all_events(session)
    all_events_list = []

    for i in all_events:
        all_events_list.append(i.event_id)

    photo_folder = "data/events_photo"

    # Получение списка всех файлов в папке
    all_photos = [f for f in os.listdir(photo_folder) if os.path.isfile(os.path.join(photo_folder, f))]

    # Определение файлов, которые нужно удалить
    photos_to_delete = [photo for photo in all_photos if int(photo.split(".")[0]) not in all_events_list]

    # Удаление файлов
    for photo in photos_to_delete:
        photo_path = os.path.join(photo_folder, photo)
        try: os.remove(photo_path)
        except: pass




@session_db
async def events_commit(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()

    event_id = data["event_id"]
    title = data["title"]
    text = data["text"]
    price = data["price"]
    text_success = data["text_success"]

    await Events.register(event_id, title, text, price, text_success, session)

    await state.finish()

    await events(message)

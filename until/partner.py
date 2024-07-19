from create_bot import bot
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import packets, table_data
from data.texts import one_stage_partner_text, two_stage_partner_text
from db.models import Person


def get_highest_title(packet: str, personal: int, general: int):
    highest_title = None

    packets_hierarchy = list(packets.keys())

    for data in table_data:
        if packets_hierarchy.index(packet) >= packets_hierarchy.index(data["packet"]) and data[
            "personal"] <= personal and data["general"] <= general:
            highest_title = data["title"]

    return highest_title


def find_index_by_title(title):
    for index, data in enumerate(table_data):
        if data["title"] == title:
            return index


async def send_text_update_status(user_id: int, title: str):
    index = find_index_by_title(title)

    if index <= 2:
        text = one_stage_partner_text
    else:
        text = two_stage_partner_text

    if text:
        await bot.send_message(user_id, text.format(title))


async def update_title(person: Person, session: AsyncSession):
    packet = person.packet
    personal = person.turnover_first_line
    general = person.total_turnover

    # Получаем звание на какое заслуживает данный пользователь, с такими данными
    title = get_highest_title(packet, personal, general)

    if title != person.status:
        person.status = title

        await send_text_update_status(person.user_id, title)

        await session.commit()

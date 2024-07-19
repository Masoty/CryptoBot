import random
from datetime import datetime

from sqlalchemy import Column, BigInteger, String, FLOAT, INTEGER, BOOLEAN, ForeignKey, select, func, \
    delete, update, Integer, Float, Numeric
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import SqlAlchemyBase, session_db


class Person(SqlAlchemyBase):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)

    # Личная информация
    user_id = Column(BigInteger, unique=True)
    first_name = Column(String)
    username = Column(String, default=None)
    phone = Column(String, default=None)
    city = Column(String, default=None)

    # Информация в боте
    balance = Column(Numeric(precision=10, scale=2), default=0)
    packet = Column(String, default="FREE")
    refer = Column(BigInteger)

    # wallet
    data_register = Column(String)
    balance_all_time = Column(Numeric(precision=10, scale=2), default=0)
    balance_bank = Column(Numeric(precision=10, scale=2), default=0)
    balance_buffer_bank = Column(Numeric(precision=10, scale=2), default=0)
    balance_all_time_bank = Column(Numeric(precision=10, scale=2), default=0)
    balance_all_time_partner = Column(Numeric(precision=10, scale=2), default=0)

    # partner
    status = Column(String, default="УЧАСТНИК")

    turnover_first_line = Column(Numeric(precision=10, scale=2), default=0)
    total_turnover = Column(Numeric(precision=10, scale=2), default=0)

    one_line_referrals = Column(Integer, default=0)
    two_line_referrals = Column(Integer, default=0)
    three_line_referrals = Column(Integer, default=0)
    four_line_referrals = Column(Integer, default=0)
    five_line_referrals = Column(Integer, default=0)


    @classmethod
    async def register(cls, user_id: int, first_name: str, refer: int, username: str, session: AsyncSession):

        if await cls.is_register(user_id, session):
            return

        data_register = datetime.now().strftime("%d.%m.%Y")

        person = cls(user_id=user_id, first_name=first_name, refer=refer, username=username, data_register=data_register)

        # Добавляем объекты в сессию
        session.add(person)

        # Сохраняем изменения в базе данных
        await session.commit()

    @classmethod
    async def is_register(cls, user_id: int, session: AsyncSession):
        if not session.is_active:
            try:
                await session.begin()
            except Exception as e:
                print(e)
        result = await session.execute(select(cls).filter_by(user_id=user_id))
        ourUser = result.first()
        if ourUser:
            return True
        else:
            return False


    @classmethod
    @session_db
    async def register_ziro_acc(cls, session: AsyncSession):
        await cls.register(1, "Global", 0, username="", session=session)

    @classmethod
    async def obj(cls, user_id, session):
        if not session.is_active:
            try:
                await session.begin()
            except Exception as e:
                print(e)
        _ = await session.execute(select(cls).where(cls.user_id == user_id))
        return _.scalar()


    @classmethod
    async def get_all_users_balance_bank(cls, session: AsyncSession):
        if not session.is_active:
            try:
                await session.begin()
            except Exception as e:
                print(e)
        all_users = await session.execute(select(cls))
        return all_users.scalars().all()


    @classmethod
    @session_db
    async def add_balance(cls, user_id: int, money: int, session: AsyncSession):

        person = await cls.obj(user_id, session)
        person.balance = person.balance + money
        await session.commit()

    @classmethod
    @session_db
    async def set_packet(cls, user_id: int, packet: int, session: AsyncSession):

        person = await cls.obj(user_id, session)
        person.packet = packet
        await session.commit()




class Events(SqlAlchemyBase):
    __tablename__ = "events"

    id = Column(BigInteger, primary_key=True)

    event_id = Column(Integer, unique=True)
    text = Column(String)
    name = Column(String)
    users = Column(ARRAY(BigInteger), default=[])

    price = Column(Numeric(precision=10, scale=2), default=0)
    text_success = Column(String)

    @classmethod
    async def is_register(cls, event_id: int, session: AsyncSession):
        if not session.is_active:
            try:
                await session.begin()
            except Exception as e:
                print(e)
        result = await session.execute(select(cls).filter_by(event_id=event_id))
        ourUser = result.first()
        if ourUser:
            return True
        else:
            return False

    @classmethod
    async def register(cls, event_id: int, name: str, text: str, price: int, text_success: str, session: AsyncSession):

        if await cls.is_register(event_id, session):
            return

        event = cls(event_id=event_id, text=text, name=name, price=price, text_success=text_success)

        # Добавляем объекты в сессию
        session.add(event)

        # Сохраняем изменения в базе данных
        await session.commit()


    @classmethod
    async def get_events(cls, session: AsyncSession):
        if not session.is_active:
            try:
                await session.begin()
            except Exception as e:
                print(e)
        all_users = await session.execute(select(cls))
        return all_users.scalars().all()


    @classmethod
    async def obj(cls, event_id, session):
        if not session.is_active:
            try:
                await session.begin()
            except Exception as e:
                print(e)
        _ = await session.execute(select(cls).where(cls.event_id == event_id))
        return _.scalar()

    @classmethod
    async def delete(cls, event_id: int, session: AsyncSession):
        if not session.is_active:
            try:
                await session.begin()
            except Exception as e:
                print(e)

        stmt = delete(cls).where(cls.event_id == event_id)
        await session.execute(stmt)
        await session.commit()

    @classmethod
    async def get_all_events(cls, session: AsyncSession):
        if not session.is_active:
            try:
                await session.begin()
            except Exception as e:
                print(e)
        all_users = await session.execute(select(cls))
        return all_users.scalars().all()





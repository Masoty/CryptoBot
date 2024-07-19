# Проект Telegram Бот

Цей проект є Telegram ботом, створеним з використанням бібліотеки Aiogram для асинхронної роботи та SQLAlchemy для взаємодії з базою даних PostgresSQL. Проект має чітку структуру, спрямовану на забезпечення зрозумілості коду та його відповідності стандартам PEP-8.

## Встановлення

Для встановлення необхідних залежностей, використовуйте команду:

```bash
pip install -r requirements.txt
```

## Налаштування

1. Відкрийте файл `data/config.py`
2. Додайте необхідні налаштування для підключення до бази даних та конфігурації бота:

```
# Bot Token
TOKEN = ""

# Ю касса
account_id = 0
secret_key = ""

# CRYPTO
EMAIL_CRYPTO = ""
PASSWORD_CRYPTO = ""

# Ключ от апи сервиса по пополнению баланса (https://nowpayments.io)
API_KEY_PAYMENTS = ""

```

## Структура проекту

```
.
├── buttons
│   ├── __init__.py
│   ├── admin.py
│   ├── buttons.py
├── data
│   ├── events_photo
│   ├── photo
│   │   ├── config.json
│   │   ├── config.py
│   │   ├── texts.py
├── db
│   ├── db.py
│   ├── models.py
├── fun
│   ├── __init__.py
│   ├── view.py
├── handlers
│   ├── edit.py
│   ├── events_admin.py
│   ├── main.py
│   ├── other.py
│   ├── register_handlers.py
│   ├── user_admin.py
├── until
│   ├── __init__.py
│   ├── bank.py
│   ├── chat_admin.py
│   ├── crypto.py
│   ├── events.py
│   ├── kassa.py
│   ├── others.py
│   ├── partner.py
│   ├── text.py
│   ├── user_admin.py
├── README.md
├── create_bot.py
├── main.py
└── requirements.txt

```

### Опис основних файлів і директорій:

- `buttons/`: Директорія з файлами, що відповідають за кнопки в боті
  - `__init__.py`: Ініціалізація модуля
  - `admin.py`: Кнопки для адміністраторів
  - `buttons.py`: Основні кнопки
- `data/`: Директорія з даними для бота
  - `events_photo/`: Директорія з подіями фотографій
  - `photo/`: Директорія з фотографіями
    - `config.json`: Конфігураційний файл
    - `config.py`: Файл конфігурації
    - `texts.py`: Тексти для повідомлень
- `db/`: Директорія з файлами бази даних
  - `db.py`: Налаштування та підключення до бази даних
  - `models.py`: Визначення моделей SQLAlchemy для бази даних
- `fun/`: Директорія з додатковими функціями
  - `__init__.py`: Ініціалізація модуля
  - `view.py`: Відображення функцій
- `handlers/`: Директорія з файлами хендлерів для обробки команд та повідомлень бота
  - `edit.py`: Хендлери для редагування
  - `events_admin.py`: Хендлери для адміністраторських подій
  - `main.py`: Основні хендлери
  - `other.py`: Інші хендлери
  - `register_handlers.py`: Реєстрація хендлерів
  - `user_admin.py`: Хендлери для адміністрування користувачів
- `until/`: Директорія з допоміжними файлами
  - `__init__.py`: Ініціалізація модуля
  - `bank.py`: Банка
  - `chat_admin.py`: Файл де описані всі функції для взаєиодії з Адміністратором
  - `crypto.py`: Тут описані функції для взаємодії з криптобіржами
  - `events.py`: Допоміжні функції для Адміна
  - `kassa.py`: Фуекції для взаємодії з Екассою
  - `other.py`: Інші допоміжні функції
  - `partner.py`: Партнерська програма
  - `refers.py`: Функції для взаємодії з рефералами
  - `text.py`: Багаторазові функції для виводу тексту в боті
  - `user_admin.py`: Адмінка
- `create_bot.py`: Створення бота
- `main.py`: Точка входу в програму
- `README.md`: Опис проекту (цей файл)
- `requirements.txt`: Список необхідних залежностей
## Використання

Щоб запустити бота, використовуйте команду:

```bash
python main.py
```

## Стандарти коду

Код написаний відповідно до стандартів PEP-8 для забезпечення читаємості та зрозумілості. У проекті використовуються хендлери для обробки різних команд та подій, а також коментарі для пояснення функціональності коду.

## Приклад коду

### create_bot.py

```python
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data.config import TOKEN

storage = MemoryStorage()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)
```


### db/db.py

```python
from functools import wraps
from os import environ
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import sqlalchemy.ext.declarative as dec
from sqlalchemy.orm import sessionmaker

from data.config import postgres

SqlAlchemyBase = dec.declarative_base()

env = environ.get

__factory = None


def get_database_url() -> str:
    return f'postgresql+asyncpg://{postgres["user"]}:{postgres["password"]}@{postgres["host"]}/{postgres["database"]}'


async def global_init():
    global __factory

    if __factory:
        return
    conn_str = get_database_url()

    engine = create_async_engine(conn_str, pool_pre_ping=True)

    async with engine.begin() as conn:
        await conn.run_sync(SqlAlchemyBase.metadata.create_all)

    __factory = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

# Створеня сессії
def create_session() -> AsyncSession:
    global __factory
    return __factory()

# Хендлер для получення сессії бази данних
def session_db(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with create_session() as session:
            return await func(*args, session=session, **kwargs)

    return wrapper
```

### db/models.py

```python
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
```

### main.py

```python
# Імпорт всіх залежностей
import asyncio
from aiogram.utils import executor

from create_bot import dp

from db.db import global_init
from db.models import Person
from until import bank_updates_every_week
from handlers.register_handlers import return_handlers
from until.crypto import updates_token

# Реєстрація хендлерів
return_handlers(dp)

async def init_bot(_):
    # Ініціалізація при старті бота
    await global_init()
    await Person.register_ziro_acc()
    asyncio.create_task(bank_updates_every_week())
    asyncio.create_task(updates_token())
    print("Токен обновлен")
    print("🔥🔥🔥 Bot Started 🔥🔥🔥")

if __name__ == '__main__':
  # Запуск бота
  executor.start_polling(dp, on_startup=init_bot)
```


Цей проект є хорошим прикладом структурованого коду, що дотримується стандартів та легко підтримується і розширюється.










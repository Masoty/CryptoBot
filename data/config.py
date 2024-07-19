import logging

from aioyookassa import YooKassa

logging.basicConfig(level=logging.ERROR)

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

YKASA_CLIENT = YooKassa(secret_key, account_id)

postgres = {
    "host": "localhost",
    "database": "Asteri",
    "user": "postgres",
    "password": "admin"
}

# Стоимость пакетов в $
packets = {
    "FREE": 0,
    "LITE": 250,
    "PRO": 750,
    "VIP": 1500
}

# AS = 100 рублей
AS = 100

table_data = [
    {"title": "УЧАСТНИК", "packet": "FREE", "personal": 0, "general": 0},
    {"title": "УЧЕНИК", "packet": "LITE", "personal": 0, "general": 0},
    {"title": "ИНВЕСТОР", "packet": "PRO", "personal": 0, "general": 0},
    {"title": "АКТИВНЫЙ ИНВЕСТОР", "packet": "PRO", "personal": 250, "general": 1000},
    {"title": "ЛИДЕР ГРУППЫ", "packet": "PRO", "personal": 750, "general": 2500},
    {"title": "НАСТАВНИК", "packet": "PRO", "personal": 1500, "general": 5000},
    {"title": "АМБАССАДОР", "packet": "PRO", "personal": 3000, "general": 10000},
    {"title": "ПАРТНЕР", "packet": "VIP", "personal": 5000, "general": 25000},
    {"title": "СТАРШИЙ ПАРТНЕР", "packet": "VIP", "personal": 10000, "general": 50000},
    {"title": "УПРАВЛЯЮЩИЙ ПАРТНЕР", "packet": "VIP", "personal": 15000, "general": 100000},
    {"title": "РЕГИОНАЛЬНЫЙ ПАРТНЕР", "packet": "VIP", "personal": 25000, "general": 250000},
    {"title": "НАЦИОНАЛЬНЫЙ ПАРТНЕР", "packet": "VIP", "personal": 50000, "general": 500000},
    {"title": "МЕЖДУНАРОДНЫЙ ПАРТНЕР", "packet": "VIP", "personal": 100000, "general": 1000000},
    {"title": "ГЕНЕРАЛЬНЫЙ ПАРТНЕР", "packet": "VIP", "personal": 150000, "general": 2500000},
    {"title": "АКЦИОНЕР", "packet": "VIP", "personal": 250000, "general": 5000000},
    {"title": "СООСНОВАТЕЛЬ", "packet": "VIP", "personal": 500000, "general": 10000000}
]

installment_plan = {
    "FREE_LITE": [
        "https://link.tinkoff.ru/AJFKSYikwHp",
        "https://link.tinkoff.ru/9ccUdf4Bnsk",
        "https://link.tinkoff.ru/WKGeDfdd91"
    ],
    "FREE_PRO": [
        "https://link.tinkoff.ru/5MKpvRWJHBc",
        "https://link.tinkoff.ru/3RIo7GX1t3G",
        "https://link.tinkoff.ru/1a3iuJPBRCo"
    ],
    "FREE_VIP": [
        "https://link.tinkoff.ru/1whI8OceH5T",
        "https://link.tinkoff.ru/626ylYAKKz9",
        "https://link.tinkoff.ru/AEFQtitPgDV"
    ],
    "LITE_PRO": [
        "https://link.tinkoff.ru/5DFLBIzaH8S",
        "https://link.tinkoff.ru/3k8Z1E11mHX",
        "https://link.tinkoff.ru/1S6AS1W5P4O"
    ],
    "LITE_VIP": [
        "https://link.tinkoff.ru/3cF4rSSFC9D",
        "https://link.tinkoff.ru/2pEItilmLX8",
        "https://link.tinkoff.ru/IaSmdhb3ib"
    ],
    "PRO_VIP": [
        "https://link.tinkoff.ru/371V3oU4ZFQ",
        "https://link.tinkoff.ru/AjmALLBe5TJ",
        "https://link.tinkoff.ru/4woKSPThYcZ"
    ]
}

chats_packets_url = {
    "LITE": "https://t.me/+_fTR_j_Df2BjNWRi",
    "PRO": "https://t.me/+A50B1VuAWvU4MDZi",
    "VIP": "https://t.me/+a-EXj6bZyuY2YWRi"
}


# Список Админов в боте
admins = [
    1502101907,
    -1001550383543
]

# Админ чат
admin_chat = -1001550383543

# Системный токен, не подлежит изменению, и заполнению
# Заполняется автоматически
TOKEN_AUTHORIZATION = ""

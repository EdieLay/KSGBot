from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
import sqlite3


chat_resps = {}


class NewResponsible(StatesGroup):
    responsible = State()
    confirm = State()


class RemovingResponsible(StatesGroup):
    responsible = State()
    confirm = State()


class BrigadeReason(StatesGroup):
    reason = State()


class TableEditing(StatesGroup):
    table = State()


class ReminderOff(StatesGroup):
    confirming = State()


class ChangeBDays(StatesGroup):
    change = State()


class CallbackAdminFilter(BaseFilter):
    def __init__(self):
        super()

    async def __call__(self, callback: CallbackQuery) -> bool:
        return await is_admin(callback.message)


class MessageAdminFilter(BaseFilter):
    def __init__(self):
        super()

    async def __call__(self, message: Message) -> bool:
        return await is_admin(message)


class CallbackRespFilter(BaseFilter):
    def __init__(self):
        super()

    async def __call__(self, callback: CallbackQuery) -> bool:
        print(callback.from_user.username)
        resps = chat_resps[callback.message.chat.id]
        print(callback.from_user.username in resps)
        return callback.from_user.username in resps


class MessageRespFilter(BaseFilter):
    def __init__(self):
        super()

    async def __call__(self, message: Message) -> bool:
        print(message.from_user.username)
        resps = chat_resps[message.chat.id]
        print(message.from_user.username in resps)
        return message.from_user.username in resps


async def is_admin(message: Message):
    id = message.from_user.id
    admins = await message.chat.get_administrators()
    ids = list(map(lambda admin: admin.user.id, admins))
    return id in ids


def refresh_responsibles():
    con = sqlite3.connect('chats.db')
    cur = con.cursor()
    cur.execute('SELECT username, chat_id FROM responsibles')
    resps = cur.fetchall()
    global chat_resps
    chat_resps = {}
    for resp in resps:
        username = resp[0]
        chat_id = resp[1]
        chat_resps.setdefault(chat_id, []) # дефолтная инициализация словаря пустым списком
        chat_resps[chat_id].append(username) # добавление в список
    cur.close()
    con.close()


def get_chat_resps():
    return chat_resps

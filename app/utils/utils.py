from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
import aiogram.exceptions
import sqlite3


chats_answers = {}


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
        return callback.from_user.username in get_responsible(callback.message.chat.id)


class MessageRespFilter(BaseFilter):
    def __init__(self):
        super()

    async def __call__(self, message: Message) -> bool:
        return message.from_user.username in get_responsible(message.chat.id)


async def is_admin(message: Message):
    id = message.from_user.id
    chat_id = message.chat.id
    try:
        admins = await message.chat.get_administrators()
    except aiogram.exceptions.TelegramForbiddenError:
        delete_chat(chat_id)
        return False
    ids = list(map(lambda admin: admin.user.id, admins))
    return id in ids


def get_responsible(chat_id):
    con = sqlite3.connect('chats.db')
    cur = con.cursor()
    cur.execute(f'SELECT username FROM responsibles WHERE chat_id={chat_id}')
    rows = cur.fetchall()
    resps = list(map(lambda row: row[0], rows))
    cur.close()
    con.close()
    return resps


def reset_chats_answers():
    con = sqlite3.connect('chats.db')
    cur = con.cursor()
    cur.execute('SELECT id FROM chats')
    chats = cur.fetchall()
    global chats_answers
    chats_answers = {}
    for chat in chats:
        chat_id = chat[0]
        chats_answers[chat_id] = False
    cur.close()
    con.close()


def delete_chat_answer(chat_id):
    chats_answers.pop(chat_id, None)


def add_chat_answer(chat_id):
    chats_answers[chat_id] = False


def set_chat_answer(chat_id):
    chats_answers[chat_id] = True


def get_chat_answer(chat_id):
    return chats_answers[chat_id]


def check_reminder_is_on(chat_id):
    con = sqlite3.connect('chats.db')
    cur = con.cursor()
    cur.execute(f'SELECT * FROM chats where id = {chat_id}')
    rows = cur.fetchall()
    cur.close()
    con.close()
    return bool(len(rows))


def delete_chat(chat_id):
    con = sqlite3.connect('chats.db')
    cur = con.cursor()
    con.execute('PRAGMA foreign_keys = ON')
    try:
        cur.execute(f'DELETE FROM chats WHERE id = {chat_id}')
        con.commit()
        delete_chat_answer(chat_id)
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
    cur.close()
    con.close()
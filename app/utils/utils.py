from aiogram.types import Message
import aiogram.exceptions
import sqlite3
from app.utils.queries import execute_query


chats_answers = {}
chats_table_answers = {}


async def is_admin(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    try:
        admins = await message.chat.get_administrators()
    except aiogram.exceptions.TelegramForbiddenError:
        delete_chat(chat_id)
        return False
    ids = list(map(lambda admin: admin.user.id, admins))
    return id in ids


def get_responsible(chat_id):
    rows = execute_query(f'SELECT username FROM responsibles WHERE chat_id={chat_id}')
    resps = list(map(lambda row: row[0], rows))
    return resps


def reset_chats_answers():
    chats = execute_query('SELECT id FROM chats')
    global chats_answers
    global chats_table_answers
    chats_answers = {}
    chats_table_answers = {}
    for chat in chats:
        chat_id = chat[0]
        chats_answers[chat_id] = False
        chats_table_answers[chat_id] = False


def delete_chat_answer(chat_id):
    chats_answers.pop(chat_id, None)


def add_chat_answer(chat_id):
    chats_answers[chat_id] = False


def set_chat_answer(chat_id):
    chats_answers[chat_id] = True


def get_chat_answer(chat_id):
    return chats_answers[chat_id]


def delete_chat_table_answer(chat_id):
    chats_table_answers.pop(chat_id, None)


def add_chat_table_answer(chat_id):
    chats_table_answers[chat_id] = False


def set_chat_table_answer(chat_id):
    chats_table_answers[chat_id] = True


def get_chat_table_answer(chat_id):
    return chats_table_answers[chat_id]


def check_reminder_is_on(chat_id):
    rows = execute_query(f'SELECT * FROM chats where id = {chat_id}')
    return bool(len(rows))


def delete_chat(chat_id):
    try:
        execute_query(f'DELETE FROM chats WHERE id = {chat_id}')
        delete_chat_answer(chat_id)
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
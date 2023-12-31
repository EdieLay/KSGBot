from aiogram.types import Message
import aiogram.exceptions
import sqlite3

from app.utils.queries import execute_query
import app.keyboards as kb


async def is_admin(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    try:
        admins = await message.chat.get_administrators()
    except aiogram.exceptions.TelegramForbiddenError:
        delete_chat(chat_id)
        return False
    ids = list(map(lambda admin: admin.user.id, admins))
    return user_id in ids


def get_responsible(chat_id):
    rows = execute_query(f'SELECT username FROM responsibles WHERE chat_id={chat_id}')
    resps = list(map(lambda row: row[0], rows))
    return resps


def reset_chats_answers():
    execute_query(f'UPDATE chats SET brigade_answered = 0, table_answered = 0, new_work_answered = 0')


def set_brigade_answer(chat_id):
    execute_query(f'UPDATE chats SET brigade_answered = 1 WHERE id = {chat_id}')


def set_table_answer(chat_id):
    execute_query(f'UPDATE chats SET table_answered = 1 WHERE id = {chat_id}')


def set_new_work_answer(chat_id):
    execute_query(f'UPDATE chats SET new_work_answered = 1 WHERE id = {chat_id}')


def check_reminder_is_on(chat_id):
    rows = execute_query(f'SELECT * FROM chats where id = {chat_id}')
    return bool(len(rows))


def delete_chat(chat_id):
    try:
        execute_query(f'DELETE FROM chats WHERE id = {chat_id}')
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)


async def remind_later(message: Message):
    resps = get_responsible(message.chat.id)
    await message.answer(f'@{" @".join(resps)}\n'
                   f'Уточните, пожалуйста, все ли рабочие заняли свои места сегодня?', reply_markup=kb.remind_later)
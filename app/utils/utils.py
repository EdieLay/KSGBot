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


def get_responsible(chat_id, is_requests=False):
    if is_requests:
        help_rows = execute_query(f'SELECT parent_chat_id FROM chats_requests WHERE id={chat_id}')
        if help_rows:
            chat_id = help_rows[0][0]
    rows = execute_query(f'SELECT username FROM responsibles WHERE chat_id={chat_id}')
    resps = list(map(lambda row: row[0], rows))
    return resps


def get_construction_managers(chat_id, is_requests = False):
    if is_requests:
        help_rows = execute_query(f'SELECT parent_chat_id FROM chats_requests WHERE id={chat_id}')
        if help_rows:
            chat_id = help_rows[0][0]
    rows = execute_query(f'SELECT username FROM construction_managers WHERE chat_id={chat_id}')
    resps = list(map(lambda row: row[0], rows))
    return resps


def reset_chats_answers():
    execute_query(f'UPDATE chats SET brigade_answered = 0, table_answered = 0, new_work_answered = 0, '
                  f'morning_plan_answered = 0, night_payment_answered = 0, day_payment_answered = 0, '
                  f'tomorrow_plan_answered = 0, evening_plan_answered = 0')
    execute_query(f'UPDATE chats_requests SET tmc_yesterday_answered = 0')


def set_answer(chat_id, field):
    execute_query(f'UPDATE chats SET {field} = 1 WHERE id = {chat_id}')


def set_requests_answer(chat_id, field):
    execute_query(f'UPDATE chats_requests SET {field} = 1 WHERE id = {chat_id}')


def check_reminder_is_on(chat_id):
    rows = execute_query(f'SELECT * FROM chats where id = {chat_id}')
    return bool(len(rows))


def check_requests_is_on(chat_id):
    rows = execute_query(f'SELECT * FROM chats_requests where id = {chat_id}')
    return bool(len(rows))


def delete_chat(chat_id):
    try:
        execute_query(f'DELETE FROM chats WHERE id = {chat_id}')
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)


def delete_requests_chat(chat_id):
    try:
        execute_query(f'DELETE FROM chats_requests WHERE id = {chat_id}')
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)


async def remind_later(message: Message):
    resps = get_responsible(message.chat.id)
    await message.answer(f'@{" @".join(resps)}\n'
                   f'Уточните, пожалуйста, все ли рабочие заняли свои места сегодня?', reply_markup=kb.remind_later)
from datetime import datetime
from aiogram import Bot
import aiogram.exceptions
import sqlite3
import csv
import os.path

import app.keyboards as kb
from app.utils.queries import execute_query
from app.utils.utils import get_responsible, delete_chat

brigade_messages = {}
table_messages = {}
new_work_messages = {}

# функция отправки напоминаний
async def brigade_report(bot: Bot):
    chats = execute_query('SELECT id, brigade_answered FROM chats')
    for chat in chats:
        chat_id = chat[0]
        answered = chat[1]
        global brigade_messages  # предыдущее сообщение с напоминанием
        if answered == 0:
            resps = get_responsible(chat_id)
            if len(resps) == 0:
                message = ('Вы включили напоминание, но не добавили ответственных. '
                           'Пожалуйста, сделайте это через команду /reminder')
                reply_markup = None
            else:
                message = (f'@{" @".join(resps)}\n'
                           f'Уточните, пожалуйста, все ли рабочие вышли сегодня на объект?\n')
                reply_markup = kb.brigade_report
            try:
                message_to_delete = brigade_messages.get(chat_id)
                if message_to_delete is not None:
                    await bot.delete_message(chat_id, message_to_delete)  # удаляем предыдущее сообщение, чтобы не спамить
                new_message = await bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
                brigade_messages[chat_id] = new_message.message_id  # сохраняем новое сообщение
            except aiogram.exceptions.TelegramForbiddenError:
                delete_chat(chat_id)
        else:  # если уже ответили, то удалять сообщение не нужно, поэтому убираем из словаря
            if chat_id in brigade_messages:
                del brigade_messages[chat_id]


async def table_update(bot: Bot):
    chats = execute_query(f'SELECT id, spreadsheet, table_answered FROM chats')
    for chat in chats:
        chat_id = chat[0]
        spreadsheet = chat[1]
        answered = chat[2]
        global table_messages
        if answered == 0:
            resps = get_responsible(chat_id)
            if spreadsheet is not None and len(resps) > 0:
                try:
                    message_to_delete = table_messages.get(chat_id)
                    if message_to_delete is not None:
                        await bot.delete_message(chat_id, message_to_delete)  # удаляем предыдущее сообщение, чтобы не спамить
                    new_message = await bot.send_message(chat_id=chat_id,
                                                         text=f'@{" @".join(resps)}\n'
                                                              f'Добрый день!😊\n'
                                                              f'Прошу обновить списки сотрудников на объекте.\n'
                                                              f'Дедлайн сегодня до 18:00🕰\n'
                                                              f'Напоминание будет приходить каждые два часа, пока не нажата кнопка "Таблица обновлена".\n'
                                                              f'{spreadsheet}', reply_markup=kb.table_reminder)
                    table_messages[chat_id] = new_message.message_id  # сохраняем новое сообщение
                except aiogram.exceptions.TelegramForbiddenError:
                    delete_chat(chat_id)
        else:  # если уже ответили, то удалять сообщение не нужно, поэтому убираем из словаря
            if chat_id in table_messages:
                del table_messages[chat_id]


async def bd_today(bot: Bot):
    chats = execute_query('SELECT id FROM chats')
    for chat in chats:
        chat_id = chat[0]
        path = f'files/{chat_id}.csv'
        if os.path.exists(path):
            file = open(path, encoding='cp1251')
            file_reader = csv.reader(file, delimiter=';')
            line_count = 0
            for row in file_reader:
                if line_count != 0:
                    bday = row[2]
                    bdaydate = datetime.strptime(bday, '%d.%m.%Y')
                    today = datetime.today()
                    if bdaydate.day == today.day and bdaydate.month == today.month:
                        try:
                            await bot.send_message(chat_id=chat_id,
                                                   text=f'Сегодня свой день рождения празднует {row[0]} @{row[1]}!🎉\nДавайте поздравим!')
                        except aiogram.exceptions.TelegramForbiddenError:
                            delete_chat(chat_id)
                            file.close()
                            os.remove(path)
                            break
                line_count += 1
            file.close()


async def new_work(bot: Bot):
    chats = execute_query('SELECT id, new_work_answered FROM chats')
    for chat in chats:
        chat_id = chat[0]
        answered = chat[1]
        global new_work_messages
        if answered == 0:
            resps = get_responsible(chat_id)
            if len(resps) > 0:
                resps_mes = f'@{" @".join(resps)} '
            else:
                resps_mes = ''
            try:
                message_to_delete = new_work_messages.get(chat_id)
                if message_to_delete is not None:
                    await bot.delete_message(chat_id, message_to_delete)  # удаляем предыдущее сообщение, чтобы не спамить
                new_message = await bot.send_message(chat_id=chat_id,
                                                     text=f'{resps_mes}@KonstantinSoleniy\n'
                                                          f'Уточните, пожалуйста, в ближайшее время планируется новый вид работ на объекте?\n'
                                                          f'Нуждаетесь в поиске новых работников?',
                                                     reply_markup=kb.new_work)
                new_work_messages[chat_id] = new_message.message_id  # сохраняем новое сообщение
            except aiogram.exceptions.TelegramForbiddenError:
                delete_chat(chat_id)
        else:  # если уже ответили, то удалять сообщение не нужно, поэтому убираем из словаря
            if chat_id in new_work_messages:
                del new_work_messages[chat_id]



from datetime import datetime
from aiogram import Bot
import aiogram.exceptions
import csv
import os.path

import app.keyboards as kb
from app.utils.queries import execute_query
from app.utils.utils import get_responsible, delete_chat

table_messages = {}
new_work_messages = {}


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
                                                              f'Прошу обновить списки сотрудников на объекте.\n'
                                                              f'Дедлайн сегодня до 18:00\n'
                                                              f'<a href=\"{spreadsheet}\">ССЫЛКА НА ТАБЛИЦУ</a>',
                                                         reply_markup=kb.table_reminder, parse_mode='HTML',
                                                         disable_web_page_preview=True)
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
                                                     text=f'{resps_mes}\n'
                                                          f'Уточните, пожалуйста, в ближайшее время планируется новый вид работ на объекте?\n'
                                                          f'Нуждаетесь в поиске новых работников?',
                                                     reply_markup=kb.new_work)
                new_work_messages[chat_id] = new_message.message_id  # сохраняем новое сообщение
            except aiogram.exceptions.TelegramForbiddenError:
                delete_chat(chat_id)
        else:  # если уже ответили, то удалять сообщение не нужно, поэтому убираем из словаря
            if chat_id in new_work_messages:
                del new_work_messages[chat_id]
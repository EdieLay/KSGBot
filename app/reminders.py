from datetime import datetime
from aiogram import Bot
import aiogram.exceptions
import sqlite3
import csv
import os.path

import app.keyboards as kb
from app.utils.queries import execute_query
from app.utils.utils import get_responsible, delete_chat


# функция отправки напоминаний
async def brigade_report(bot: Bot):
    chats = execute_query('SELECT id, brigade_answered FROM chats')
    for chat in chats:
        chat_id = chat[0]
        answered = chat[1]
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
                await bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
            except aiogram.exceptions.TelegramForbiddenError:
                delete_chat(chat_id)


async def table_update(bot: Bot):
    chats = execute_query(f'SELECT id, spreadsheet, table_answered FROM chats')
    for chat in chats:
        chat_id = chat[0]
        spreadsheet = chat[1]
        answered = chat[2]
        if answered == 0:
            resps = get_responsible(chat_id)
            if spreadsheet != None and len(resps) > 0:
                try:
                    await bot.send_message(chat_id=chat_id, text=f'@{" @".join(resps)}\n'
                                                                 f'Добрый день!😊\n'
                                                                 f'Прошу обновить списки сотрудников на объекте.\n'
                                                                 f'Дедлайн сегодня до 18:00🕰\n'
                                                                 f'Напоминание будет приходить каждые два часа, пока не нажата кнопка "Таблица обновлена".\n'
                                                                 f'{spreadsheet}', reply_markup=kb.table_reminder)
                except aiogram.exceptions.TelegramForbiddenError:
                    delete_chat(chat_id)


async def bd_today(bot: Bot):
    con = sqlite3.connect('chats.db')
    cur = con.cursor()
    cur.execute(f'SELECT id FROM chats')
    chats = cur.fetchall()
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
    cur.close()
    con.close()




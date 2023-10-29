from datetime import datetime
from aiogram import Bot
import aiogram.exceptions
import sqlite3
import csv
import os.path

import app.keyboards as kb
from app.utils.utils import get_chat_resps, refresh_responsibles


# функция отправки напоминаний
async def brigade_report(bot: Bot):
    if datetime.today().weekday() < 7:
        chat_items = get_chat_resps().items()
        for chat_id, responsibles in chat_items:
            try:
                await bot.send_message(chat_id=chat_id, text=f'@{" @".join(responsibles)}\nВышла ли бригада?', reply_markup=kb.brigade_report)
            except aiogram.exceptions.TelegramForbiddenError:
                delete_chat(chat_id)


async def table_update(bot: Bot):
    chat_items = get_chat_resps().items()
    for chat_id, responsibles in chat_items:
        con = sqlite3.connect('chats.db')
        cur = con.cursor()
        con.execute('PRAGMA foreign_keys = ON')
        cur.execute(f'SELECT spreadsheet FROM chats WHERE chats.id = {chat_id}')
        spreadsheet = (cur.fetchone())[0]
        if spreadsheet != None:
            try:
                await bot.send_message(chat_id=chat_id, text=f'@{" @".join(responsibles)}\nОбновите список сотрудников на объекте\nДедлайн сегодня до 18:00\n{spreadsheet}')
            except aiogram.exceptions.TelegramForbiddenError:
                delete_chat(chat_id)


async def bd_today(bot: Bot):
    chat_items = get_chat_resps().keys()
    for chat_id in chat_items:
        path = f'files/{chat_id}.csv'
        if os.path.exists(path):
            file = open(path)
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


def delete_chat(chat_id):
    con = sqlite3.connect('chats.db')
    cur = con.cursor()
    con.execute('PRAGMA foreign_keys = ON')
    try:
        cur.execute(f'DELETE FROM chats WHERE id = {chat_id}')
        con.commit()
        refresh_responsibles()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
    cur.close()
    con.close()
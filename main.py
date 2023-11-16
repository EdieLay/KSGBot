import asyncio
from aiogram import Bot, Dispatcher, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import sqlite3
import os
from datetime import datetime, timedelta

import app.handlers as hnd
from app.handlers import adminRouter, respRouter
import app.reminders as rem
from app.utils.utils import reset_chats_answers

# добавить контроль release/dev через переменную
bot = Bot('6678317099:AAH850dSpV7hr-VC0GpijLoYOpiegkBcgKs')  # release
# bot = Bot('6918424612:AAFfcmvsTNnVc1FFz908PgLuowo9Djzo62c')  # dev


@adminRouter.message(hnd.F.document, hnd.ChangeBDays.change)
async def change_bdays(message: hnd.Message, state: hnd.FSMContext):
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    chat_id = message.chat.id
    path = f'files/{chat_id}.csv'
    await bot.download_file(file_path, path)
    await message.answer('Файл обновлён')
    await state.clear()


async def set_commands():
    commands = [
        types.BotCommand(command='start', description='Начальная установка'),
        types.BotCommand(command='reminder', description='Управление напоминаниями'),
        types.BotCommand(command='birthday', description='Управление днями рождения'),
        types.BotCommand(command='brigadeok', description='Сообщить о выходе бригад')
    ]
    await bot.set_my_commands(commands, types.BotCommandScopeDefault())


async def main():
    con = sqlite3.connect('chats.db')
    cur = con.cursor()
    con.execute('PRAGMA foreign_keys = ON')
    cur.execute('CREATE TABLE IF NOT EXISTS chats (id integer primary key, spreadsheet text null)')
    cur.execute('CREATE TABLE IF NOT EXISTS responsibles (id integer primary key autoincrement, username text not null, chat_id integer, foreign key(chat_id) references chats(id) on delete cascade)')
    con.commit()
    cur.close()
    con.close()

    reset_chats_answers()

    dp = Dispatcher()
    dp.include_router(adminRouter)
    dp.include_router(respRouter)
    await set_commands()

    if not os.path.exists('files'):
        os.mkdir('files')

    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.add_job(rem.brigade_report, trigger='cron', day_of_week='mon-fri', hour='10-23', start_date=datetime.now(), kwargs={'bot': bot})
    scheduler.add_job(rem.table_update, trigger='cron', day_of_week='thu', hour='11-18/2', start_date=datetime.now(), kwargs={'bot': bot})
    scheduler.add_job(rem.bd_today, trigger='cron', hour=10, minute=10, start_date=datetime.now(), kwargs={'bot': bot})
    scheduler.add_job(reset_chats_answers, trigger='cron', hour=1, minute=0, start_date=datetime.now())
    #scheduler.add_job(rem.brigade_report, trigger='date', run_date=datetime.now() + timedelta(seconds=5), kwargs={'bot': bot})
    #scheduler.add_job(rem.table_update, trigger='date', run_date=datetime.now() + timedelta(seconds=10), kwargs={'bot': bot})
    #scheduler.add_job(rem.bd_today, trigger='date', run_date=datetime.now() + timedelta(seconds=15), kwargs={'bot': bot})
    #scheduler.add_job(reset_chats_answers, trigger='date', run_date=datetime.now() + timedelta(seconds=5))
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')

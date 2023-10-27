import asyncio
from aiogram import Bot, Dispatcher, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import sqlite3
from datetime import datetime, timedelta

from app.handlers import adminRouter, respRouter
import app.reminders as rem
from app.utils.utils import refresh_responsibles


async def set_commands(bot: Bot):
    commands = [
        types.BotCommand(command='start', description='Начальная установка'),
        types.BotCommand(command='reminder', description='Управление напоминаниями'),
        types.BotCommand(command='birthday', description='Управление днями рождения'),
    ]
    await bot.set_my_commands(commands, types.BotCommandScopeDefault())

async def main():
    con = sqlite3.connect('chats.db')
    cur = con.cursor()
    con.execute('PRAGMA foreign_keys = ON')
    cur.execute('CREATE TABLE IF NOT EXISTS chats (id integer primary key, spreadsheet text null)')
    cur.execute('CREATE TABLE IF NOT EXISTS responsibles (id integer primary key autoincrement, username text not null, chat_id integer, foreign key(chat_id) references chats(id) on delete cascade)')
    cur.execute('CREATE TABLE IF NOT EXISTS birthdays (id integer primary key autoincrement, name text not null, birthday text not null, chat_id integer, foreign key(chat_id) references chats(id) on delete cascade)')
    con.commit()
    cur.close()
    con.close()

    refresh_responsibles()  # подключнеие к бд и занесение в список всех ответственных

    bot = Bot('6678317099:AAH850dSpV7hr-VC0GpijLoYOpiegkBcgKs')
    dp = Dispatcher()
    dp.include_router(adminRouter)
    dp.include_router(respRouter)
    await set_commands(bot)

    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    #scheduler.add_job(rem.brigade_report, trigger='cron', hour=15, minute=45, start_date=datetime.now(), kwargs={'bot': bot})
    #scheduler.add_job(rem.table_update, trigger='cron', day=4, hour=15, minute=52, start_date=datetime.now(), kwargs={'bot': bot})
    scheduler.add_job(rem.brigade_report, trigger='date', run_date=datetime.now() + timedelta(seconds=10), kwargs={'bot': bot})
    scheduler.add_job(rem.table_update, trigger='date', run_date=datetime.now() + timedelta(seconds=5), kwargs={'bot': bot})
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')

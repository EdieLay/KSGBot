import asyncio
from aiogram import Bot, Dispatcher, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import sqlite3
import os

import app.handlers as hnd
from app.handlers import adminRouter, respRouter
from app.utils.utils import reset_chats_answers
from app.scheduler import add_default_jobs, start_scheduler, add_dev_jobs

version = 'release'
if 'release' == version:
    bot = Bot('6678317099:AAH850dSpV7hr-VC0GpijLoYOpiegkBcgKs')  # release
else:
    bot = Bot('6918424612:AAFfcmvsTNnVc1FFz908PgLuowo9Djzo62c')  # dev


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
    cur.execute('CREATE TABLE IF NOT EXISTS chats (id integer primary key, spreadsheet text null, brigade_answered integer default 1 not null, table_answered integer default 1 not null)')
    cur.execute('CREATE TABLE IF NOT EXISTS responsibles (id integer primary key autoincrement, username text not null, chat_id integer, foreign key(chat_id) references chats(id) on delete cascade)')
    con.commit()
    cur.close()
    con.close()

    dp = Dispatcher()
    dp.include_router(adminRouter)
    dp.include_router(respRouter)
    await set_commands()

    if not os.path.exists('files'):
        os.mkdir('files')

    if 'release' == version:
        add_default_jobs(bot)
    else:
        reset_chats_answers()
        add_dev_jobs(bot)
    start_scheduler()

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')

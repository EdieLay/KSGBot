import asyncio
from aiogram import Bot, Dispatcher, types
import sqlite3
import os

import app.handlers.commands as cmds
from app.handlers.routers import adminRouter, respRouter
from app.utils.utils import reset_chats_answers
from app.scheduler import add_default_jobs, start_scheduler, add_dev_jobs
from tokens import release_token, dev_token

version = 'release'
if 'release' == version:
    bot = Bot(release_token)  # release
else:
    bot = Bot(dev_token)  # dev


@adminRouter.message(cmds.F.document, cmds.ChangeBDays.change)
async def change_bdays(message: cmds.Message, state: cmds.FSMContext):
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    chat_id = message.chat.id
    path = f'files/{chat_id}.csv'
    await bot.download_file(file_path, path)
    await message.answer('Файл обновлён')
    await state.clear()


@adminRouter.callback_query(cmds.F.data == 'requests_on')
async def requests_on(callback: cmds.CallbackQuery):
    chat_id = callback.message.chat.id
    chat_name = callback.message.chat.title
    object_name = (chat_name.split(' '))[-1].lower().strip()
    if not cmds.check_requests_is_on(chat_id):
        parent_chats = cmds.execute_query('SELECT id FROM chats')
        for parent_chat in parent_chats:
            parent_id = parent_chat[0]
            chat = await bot.get_chat(parent_id)
            parent_name = chat.title
            parent_object_name = (parent_name.split(' '))[-1].lower().strip()
            if object_name == parent_object_name:
                cmds.execute_query(f'INSERT INTO chats_requests (id, parent_chat_id) VALUES ({chat_id}, {parent_id})')
                await callback.message.edit_text('Напоминание включено.', reply_markup=cmds.kb.requests)
                await callback.answer()
                return
        await callback.message.answer('Не было найдено соответствующего чата объекта.', reply_markup=cmds.kb.requests)
        await callback.answer()
        return
    else:
        await callback.answer('Напоминание уже включено')


async def set_commands():
    commands = [
        types.BotCommand(command='start', description='Начальная установка'),
        types.BotCommand(command='reminder', description='Управление напоминаниями'),
        types.BotCommand(command='requests', description='Управление "Заявками"'),
        types.BotCommand(command='birthday', description='Управление днями рождения')
    ]
    await bot.set_my_commands(commands, types.BotCommandScopeDefault())


async def main():
    con = sqlite3.connect('chats.db')
    cur = con.cursor()
    con.execute('PRAGMA foreign_keys = ON')
    cur.execute('CREATE TABLE IF NOT EXISTS chats (id integer primary key, spreadsheet text null, brigade_answered integer default 1 not null, table_answered integer default 1 not null, new_work_answered integer default 1 not null, '
                'morning_plan_answered integer default 1 not null, night_payment_answered integer default 1 not null, day_payment_answered integer default 1 not null, '
                'tomorrow_plan_answered integer default 1 not null, evening_plan_answered integer default 1 not null)')
    cur.execute('CREATE TABLE IF NOT EXISTS chats_requests (id integer primary key, parent_chat_id integer not null, spreadsheet text null, tmc_yesterday_answered integer default 1 not null, foreign key(parent_chat_id) references chats(id) on delete cascade)')
    cur.execute('CREATE TABLE IF NOT EXISTS responsibles (id integer primary key autoincrement, username text not null, chat_id integer, foreign key(chat_id) references chats(id) on delete cascade)')
    cur.execute('CREATE TABLE IF NOT EXISTS construction_managers (id integer primary key autoincrement, username text not null, chat_id integer, foreign key(chat_id) references chats(id) on delete cascade)')
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

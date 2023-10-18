from datetime import datetime
from aiogram import Bot
import aiogram.exceptions

import app.keyboards as kb


# функция отправки напоминаний
async def brigade_report(bot: Bot):
    if datetime.today().weekday() < 6:
        # прочитать базу данных, взять все id чатов
        # for chat in chats:
        responsible = 'realcaaap'
        chat_id = '423161091'
        try:
            await bot.send_message(chat_id=chat_id, text=f'@{responsible} Вышла ли бригада?', reply_markup=kb.brigade_report)
        except aiogram.exceptions.TelegramForbiddenError:
            # удаление чата из базы данных
            pass


async def table_update(bot: Bot):
    # for chat in chats:
    responsible = 'realcaaap'
    chat_id = '423161091'
    try:
        await bot.send_message(chat_id=chat_id, text=f'@{responsible} Обновите данные в таблице',
                               reply_markup=kb.brigade_report)
    except aiogram.exceptions.TelegramForbiddenError:
        # удаление чата из базы данных
        pass
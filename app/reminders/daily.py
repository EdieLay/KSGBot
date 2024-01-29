from datetime import datetime
from aiogram import Bot
import aiogram.exceptions
import csv
import os.path

import app.keyboards as kb
from app.utils.queries import execute_query
from app.utils.utils import get_responsible, get_construction_managers, delete_chat

brigade_messages = {}
morning_plan_messages = {}


async def morning_plan(bot: Bot):
    chats = execute_query('SELECT id, morning_plan_answered FROM chats')
    for chat in chats:
        chat_id = chat[0]
        answered = chat[1]
        global morning_plan_messages  # предыдущее сообщение с напоминанием
        if answered == 0:
            resps = get_responsible(chat_id)
            managers = get_construction_managers(chat_id)
            if len(resps) == 0 and len(managers) == 0:
                message = ('Вы включили напоминание, но не добавили ответственных и рук. строя. '
                           'Пожалуйста, сделайте это через команду /reminder')
                reply_markup = None
            else:
                message = (f'@{" @".join(resps)} @{" @".join(managers)}\n'
                           f'Прошу предоставить план работ/отчет о фактическом количестве людей на сегодня (с указанием даты) + фото рабочих в начале рабочего дня.\n')
                reply_markup = kb.brigade_report
            try:
                message_to_delete = morning_plan_messages.get(chat_id)
                if message_to_delete is not None:
                    await bot.delete_message(chat_id, message_to_delete)  # удаляем предыдущее сообщение, чтобы не спамить
                new_message = await bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
                morning_plan_messages[chat_id] = new_message.message_id  # сохраняем новое сообщение
            except aiogram.exceptions.TelegramForbiddenError:
                delete_chat(chat_id)
        else:  # если уже ответили, то удалять сообщение не нужно, поэтому убираем из словаря
            if chat_id in morning_plan_messages:
                del morning_plan_messages[chat_id]

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



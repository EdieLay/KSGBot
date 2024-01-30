from datetime import datetime
from aiogram import Bot
import aiogram.exceptions
import csv
import os.path

import app.keyboards as kb
from app.utils.queries import execute_query
from app.utils.utils import get_responsible, get_construction_managers, delete_chat

morning_plan_messages = {}
brigade_messages = {}
night_payment_messages = {}
day_payment_messages = {}
tomorrow_plan_messages = {}
evening_plan_messages = {}


async def del_and_send_msg(bot: Bot, chat_id, msgs, msg, markup):
    msg_to_del = msgs.get(chat_id)
    if msg_to_del is not None:
        await bot.delete_message(chat_id, msg_to_del)  # удаляем предыдущее сообщение, чтобы не спамить
    new_message = await bot.send_message(chat_id=chat_id, text=msg, reply_markup=markup)
    msgs[chat_id] = new_message.message_id  # сохраняем новое сообщение


async def morning_plan(bot: Bot):
    chats = execute_query('SELECT id, morning_plan_answered FROM chats')
    for chat in chats:
        chat_id = chat[0]
        answered = chat[1]
        global morning_plan_messages  # предыдущее сообщение с напоминанием
        if answered == 0:
            resps = get_responsible(chat_id)
            managers = get_construction_managers(chat_id)
            if len(resps) > 0 or len(managers) > 0:
                resps_str = f'@{" @".join(resps)} ' if len(resps) > 0 else ''
                managers_str = f'@{" @".join(managers)}' if len(managers) > 0 else ''
                message = (f'{resps_str}{managers_str}\n'
                           f'Прошу предоставить план работ/отчет о фактическом количестве людей на сегодня (с указанием даты) + фото рабочих в начале рабочего дня.\n')
                reply_markup = kb.morning_plan
                try:
                    await del_and_send_msg(bot, chat_id, morning_plan_messages, message, reply_markup)
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
            if len(resps) > 0:
                message = (f'@{" @".join(resps)}\n'
                           f'Уточните, пожалуйста, все ли рабочие вышли сегодня на объект?\n')
                reply_markup = kb.brigade_report
                try:
                    await del_and_send_msg(bot, chat_id, brigade_messages, message, reply_markup)
                except aiogram.exceptions.TelegramForbiddenError:
                    delete_chat(chat_id)
        else:  # если уже ответили, то удалять сообщение не нужно, поэтому убираем из словаря
            if chat_id in brigade_messages:
                del brigade_messages[chat_id]


async def night_payment(bot: Bot):
    chats = execute_query('SELECT id, night_payment_answered FROM chats')
    for chat in chats:
        chat_id = chat[0]
        answered = chat[1]
        global night_payment_messages  # предыдущее сообщение с напоминанием
        if answered == 0:
            resps = get_responsible(chat_id)
            managers = get_construction_managers(chat_id)
            if len(resps) > 0 or len(managers) > 0:
                resps_str = f'@{" @".join(resps)} ' if len(resps) > 0 else ''
                managers_str = f'@{" @".join(managers)}' if len(managers) > 0 else ''
                message = (f'{resps_str}{managers_str}\n'
                           f'Прошу подать заявку на оплату ночного дежурного + фото отчет\n')
                reply_markup = kb.night_payment
                try:
                    await del_and_send_msg(bot, chat_id, night_payment_messages, message, reply_markup)
                except aiogram.exceptions.TelegramForbiddenError:
                    delete_chat(chat_id)
        else:  # если уже ответили, то удалять сообщение не нужно, поэтому убираем из словаря
            if chat_id in night_payment_messages:
                del night_payment_messages[chat_id]


async def day_payment(bot: Bot):
    chats = execute_query('SELECT id, day_payment_answered FROM chats')
    for chat in chats:
        chat_id = chat[0]
        answered = chat[1]
        global day_payment_messages  # предыдущее сообщение с напоминанием
        if answered == 0:
            managers = get_construction_managers(chat_id)
            if len(managers) > 0:
                message = (f'@{" @".join(managers)}\n'
                           f'Просьба подать заявку на оплату подневщикам за сегодня. Заявку необходимо скинуть до 19:00\n')
                reply_markup = kb.day_payment
                try:
                    await del_and_send_msg(bot, chat_id, day_payment_messages, message, reply_markup)
                except aiogram.exceptions.TelegramForbiddenError:
                    delete_chat(chat_id)
        else:  # если уже ответили, то удалять сообщение не нужно, поэтому убираем из словаря
            if chat_id in day_payment_messages:
                del day_payment_messages[chat_id]


async def tomorrow_plan(bot: Bot):
    chats = execute_query('SELECT id, tomorrow_plan_answered FROM chats')
    for chat in chats:
        chat_id = chat[0]
        answered = chat[1]
        global tomorrow_plan_messages  # предыдущее сообщение с напоминанием
        if answered == 0:
            resps = get_responsible(chat_id)
            managers = get_construction_managers(chat_id)
            if len(resps) > 0 and len(managers) > 0:
                resps_str = f'@{" @".join(resps)} ' if len(resps) > 0 else ''
                managers_str = f'@{" @".join(managers)}' if len(managers) > 0 else ''
                message = (f'{resps_str}{managers_str}\n'
                           f'Прошу предоставить план работ/отчет о фактическом количестве людей на завтра (с указанием даты).\n')
                reply_markup = kb.tomorrow_plan
                try:
                    await del_and_send_msg(bot, chat_id, tomorrow_plan_messages, message, reply_markup)
                except aiogram.exceptions.TelegramForbiddenError:
                    delete_chat(chat_id)
        else:  # если уже ответили, то удалять сообщение не нужно, поэтому убираем из словаря
            if chat_id in tomorrow_plan_messages:
                del tomorrow_plan_messages[chat_id]


async def evening_plan(bot: Bot):
    chats = execute_query('SELECT id, evening_plan_answered FROM chats')
    for chat in chats:
        chat_id = chat[0]
        answered = chat[1]
        global evening_plan_messages  # предыдущее сообщение с напоминанием
        if answered == 0:
            resps = get_responsible(chat_id)
            managers = get_construction_managers(chat_id)
            if len(resps) > 0 or len(managers) > 0:
                resps_str = f'@{" @".join(resps)} ' if len(resps) > 0 else ''
                managers_str = f'@{" @".join(managers)}' if len(managers) > 0 else ''
                message = (f'{resps_str}{managers_str}\n'
                           f'Прошу предоставить отчет о проделанной работе за сегодня: фото до/после + заявка на оплату с полным описанием выполненных видов работ.\n')
                reply_markup = kb.evening_plan
                try:
                    await del_and_send_msg(bot, chat_id, evening_plan_messages, message, reply_markup)
                except aiogram.exceptions.TelegramForbiddenError:
                    delete_chat(chat_id)
        else:  # если уже ответили, то удалять сообщение не нужно, поэтому убираем из словаря
            if chat_id in evening_plan_messages:
                del evening_plan_messages[chat_id]



import csv
import os.path

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import sqlite3

import app.keyboards as kb
from app.utils.queries import execute_query
from app.utils.states import (NewResponsible, RemovingResponsible,
                              TableEditing, ReminderOff, ChangeBDays)
from app.utils.utils import check_reminder_is_on, get_responsible

commandsRouter = Router()


# запуск бота
@commandsRouter.message(Command('start'))
async def start(message: Message):
    await message.answer('Приветствую! Я буду помогать вам в процессе работы!')


# Меню напоминания
@commandsRouter.message(Command('reminder'))
async def reminder(message: Message):
    await message.answer('Что нужно сделать с напоминанием?', reply_markup=kb.reminder)


@commandsRouter.message(Command('birthday'))
async def birthday(message: Message, state: FSMContext):
    chat_id = message.chat.id
    path = f'files/{chat_id}.csv'
    if not os.path.exists(path):
        file = open(path, 'w+', encoding='cp1251', errors='replace')
        file_writer = csv.writer(file, delimiter=';', lineterminator='\r')
        file_writer.writerow(['Имя Фамилия', 'Имя пользователя (без @)', 'Дата рождения (ДД.ММ.ГГГГ)'])
        file.close()
    file = FSInputFile(path)
    await message.answer_document(file)
    await message.answer('Это текущая таблица дней рождения.\n'
                         'Скачайте её, отредактируйте и отправьте', reply_markup=kb.change_bdays)
    await state.set_state(ChangeBDays.change)


@commandsRouter.callback_query(F.data == 'bdays_not_changed')
async def birthday_nochanges(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Дни рождения остались без изменений')
    await state.clear()


# Включить напоминание
@commandsRouter.callback_query(F.data == 'reminder_on')
async def reminder_on(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    if not check_reminder_is_on(chat_id):
        try:
            execute_query(f'INSERT INTO chats (id) VALUES ({chat_id})')
            await callback.message.edit_text('✅Напоминание включено✅', reply_markup=kb.reminder)
            await callback.answer('Напоминание включено')
        except sqlite3.Error:
            await callback.message.answer('❌Не удалось включить напоминание❌', reply_markup=kb.reminder)
            await callback.answer('Не удалось включить напоминание')
    else:
        await callback.answer('Напоминание уже включено')


# Отключить напомниание
@commandsRouter.callback_query(F.data == 'reminder_off')
async def reminder_off(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    if not check_reminder_is_on(chat_id):
        await callback.message.edit_text('⚠️Напоминание ещё не было включено⚠️', reply_markup=kb.reminder)
        await callback.answer('')
    else:
        await callback.message.edit_text('При отключении напоминания вся информация об ответственных и днях рождения будет удалена!\n'
                                      'Введите "Подтверждаю", чтобы отключить напоминание.\n'
                                      'Введите любое другое сообщение, чтобы отменить.', reply_markup=kb.cancel)
        await callback.answer('')
        await state.set_state(ReminderOff.confirming)


@commandsRouter.callback_query(ReminderOff.confirming, F.data == 'cancel')
async def reminder_off_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('⚠️Напоминание НЕ было выключено⚠️', reply_markup=kb.reminder)
    await callback.answer('')
    await state.clear()


@commandsRouter.message(ReminderOff.confirming)
async def reminder_off_confirming(message: Message, state: FSMContext):
    if message.text.strip().lower() == 'подтверждаю':
        try:
            execute_query(f'DELETE FROM chats WHERE id = {message.chat.id}')
            await message.answer('Напоминание выключено!')
        except sqlite3.Error:
            await message.answer('Не удалось выключить напоминание!')
    await state.clear()


# Редактировать напоминание
@commandsRouter.callback_query(F.data == 'responsible_add')
async def responsible_add(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    if check_reminder_is_on(chat_id):
        await callback.message.edit_text('Введите имя пользователя нового ответственного (без @)', reply_markup=kb.cancel)
        await callback.answer('')
        await state.set_state(NewResponsible.responsible)
    else:
        await callback.message.edit_text('⚠️Включите напоминание, чтобы добавить ответственного⚠️', reply_markup=kb.reminder)
        await callback.answer('')


@commandsRouter.callback_query(NewResponsible.responsible, F.data == 'cancel')
async def cancel_responsible(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('⚠️Отмена назначения ответственного⚠️', reply_markup=kb.reminder)
    await callback.answer('Отмена')
    await state.clear()


# Установка нового ответственного
@commandsRouter.message(NewResponsible.responsible)
async def set_responsible(message: Message, state: FSMContext):
    responsible = message.text.strip()
    await state.update_data(responsible=responsible)
    await state.set_state(NewResponsible.confirm)
    await message.answer(f'Сделать ответственным @{responsible}?', reply_markup=kb.confirm)


@commandsRouter.callback_query(NewResponsible.confirm, F.data == 'confirm_yes')
async def confirmed(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    responsible = data["responsible"]
    chat_id = callback.message.chat.id
    rows = execute_query(f'SELECT * FROM responsibles WHERE username = "{responsible}" AND chat_id = {chat_id}')
    if len(rows) == 0:
        try:
            execute_query(f'INSERT INTO responsibles (username, chat_id) VALUES ("{responsible}", {chat_id})')
            await callback.message.edit_text(f'✅Ответственным назначен @{responsible}✅', reply_markup=kb.reminder)
            await callback.answer('Ответственный назначен')
        except sqlite3.Error:
            await callback.message.answer('❌Не удалось добавить ответственного❌\nПопробуйте включить напоминание', reply_markup=kb.reminder)
            await callback.answer('')
    else:
        await callback.message.edit_text('⚠️Этот пользователь уже назначен ответственным в этом чате⚠️', reply_markup=kb.reminder)
        await callback.answer('')
    await state.clear()


# эту функцию можно совместить с responsible_add
@commandsRouter.callback_query(NewResponsible.confirm, F.data == 'confirm_no')
async def reminder_change(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('⚠️Отмена назначения ответственного⚠️', reply_markup=kb.reminder)
    await callback.answer('')
    await state.clear()


@commandsRouter.callback_query(F.data == 'responsible_remove')
async def responsible_remove(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    responsibles = get_responsible(chat_id)
    if len(responsibles) == 0:
        await callback.message.edit_text('⚠️Вы ещё не назначили ответственных, либо напоминание не включено⚠️', reply_markup=kb.reminder)
        await callback.answer('')
    else:
        resps_kb = list(map(lambda resp: [kb.InlineKeyboardButton(text=f'{resp}', callback_data=f'{resp}')], responsibles))
        resps_kb.append([kb.InlineKeyboardButton(text='Отмена', callback_data='cancel_resp')])
        resps = kb.InlineKeyboardMarkup(inline_keyboard=resps_kb)
        await state.set_state(RemovingResponsible.responsible)
        await callback.message.edit_text('Выберите пользователя', reply_markup=resps)
        await callback.answer('')


@commandsRouter.callback_query(RemovingResponsible.responsible)
async def responsible_remove_confirm(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'cancel_resp':
        await callback.message.edit_text('⚠️Отмена удаления ответственного⚠️', reply_markup=kb.reminder)
        await callback.answer('')
        await state.clear()
    elif callback.data in get_responsible(callback.message.chat.id):
        await callback.message.edit_text(f'Убрать из ответственных {callback.data}?', reply_markup=kb.confirm)
        await callback.answer('')
        await state.update_data(remove=callback.data)
        await state.set_state(RemovingResponsible.confirm)


@commandsRouter.callback_query(RemovingResponsible.confirm, F.data == 'confirm_yes')
async def responsible_remove_apply(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    responsible = data["remove"]
    chat_id = callback.message.chat.id
    try:
        execute_query(f'DELETE FROM responsibles WHERE username = "{responsible}" AND chat_id = {chat_id}')
        await callback.message.edit_text(f'✅@{responsible} удалён из ответственных✅', reply_markup=kb.reminder)
        await callback.answer('Ответственный удалён')
    except sqlite3.Error:
        await callback.message.edit_text('❌Не удалось удалить ответственного❌', reply_markup=kb.reminder)
        await callback.answer('')
    await state.clear()


@commandsRouter.callback_query(RemovingResponsible.confirm, F.data == 'confirm_no')
async def responsible_remove_declined(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('⚠️Отмена удаления ответственного⚠️', reply_markup=kb.reminder)
    await callback.answer('')
    await state.clear()


@commandsRouter.callback_query(F.data == 'table_change')
async def table_change(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    row = execute_query(f'SELECT spreadsheet FROM chats WHERE chats.id = {chat_id}')
    if len(row) == 0:
        await callback.message.edit_text('⚠️Включите напоминание, чтобы добавить таблицу⚠️', reply_markup=kb.reminder)
        await callback.answer('')
    else:
        spreadsheet = row[0][0]
        if not bool(spreadsheet):
            spreadsheet_state = 'Вы ещё не добавляли таблицу!'
        else:
            spreadsheet_state = f'Текущая таблица: {spreadsheet}'
        await state.set_state(TableEditing.table)
        await callback.message.edit_text(f'{spreadsheet_state}\nВведите ссылку на новую таблицу.', reply_markup=kb.cancel_table)
        await callback.answer('')


@commandsRouter.callback_query(TableEditing.table, F.data == 'cancel_table')
async def table_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('⚠️Отмена изменения таблицы⚠️', reply_markup=kb.reminder)
    await callback.answer('Отмена')
    await state.clear()


@commandsRouter.callback_query(TableEditing.table, F.data == 'delete_table')
async def table_delete(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    try:
        execute_query(f'UPDATE chats SET spreadsheet = null where id = {chat_id}')
        await callback.message.edit_text('✅Ссылка на таблицу удалена✅', reply_markup=kb.reminder)
        await callback.answer('')
    except sqlite3.Error:
        await callback.message.edit_text('❌Не удалось удалить ссылку на таблицу❌', reply_markup=kb.reminder)
        await callback.answer('')
    await state.clear()


@commandsRouter.message(TableEditing.table)
async def table_apply(message: Message, state: FSMContext):
    new_table = message.text.strip()
    chat_id = message.chat.id
    try:
        execute_query(f'UPDATE chats SET spreadsheet = "{new_table}" where id = {chat_id}')
        await message.answer('✅Ссылка на таблицу обновлена✅', reply_markup=kb.reminder)
    except sqlite3.Error:
        await message.answer('❌Не удалось обновить ссылку на таблицу❌')
    await state.clear()
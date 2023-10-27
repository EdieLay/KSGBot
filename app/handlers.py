from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import sqlite3

import app.keyboards as kb
from app.utils.utils import (NewResponsible, RemovingResponsible, BrigadeReason, TableEditing, ReminderOff,
                             CallbackAdminFilter, MessageAdminFilter,
                             CallbackRespFilter, MessageRespFilter,
                             refresh_responsibles)


adminRouter = Router()
adminRouter.callback_query.filter(CallbackAdminFilter())
adminRouter.message.filter(MessageAdminFilter())

respRouter = Router()
respRouter.callback_query.filter(CallbackRespFilter())
respRouter.message.filter(MessageRespFilter())


# запуск бота
@adminRouter.message(Command('start'))
async def start(message: Message):
    await message.answer(f'Приветствую, {message.chat.title}')


# Меню напоминания
@adminRouter.message(Command('reminder'))
async def reminder(message: Message):
    await message.answer('Что нужно сделать с напоминанием?', reply_markup=kb.reminder)


@adminRouter.message(Command('birthday'))
async def birthday(message: Message):
    await message.answer('Что вы хотите сделать?')

# Включить напоминание
@adminRouter.callback_query(F.data == 'reminder_on')
async def reminder_on(callback: CallbackQuery):
    con = sqlite3.connect('chats.db')
    cur = con.cursor()
    chat_id = callback.message.chat.id
    cur.execute(f'SELECT * FROM chats where id = {chat_id}')
    rows = cur.fetchall()
    if len(rows) == 0:
        try:
            cur.execute(f'INSERT INTO chats (id) VALUES ({chat_id})')
            con.commit()
            await callback.message.answer('Напоминание включено!')
            await callback.answer('')
        except sqlite3.Error as er:
            await callback.message.answer('Не удалось включить напоминание')
            await callback.answer('')
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)
    else:
        await callback.answer('Напоминание уже включено')
    cur.close()
    con.close()


# Отключить напомниание
@adminRouter.callback_query(F.data == 'reminder_off')
async def reminder_off(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('При отключении напоминания вся информация об ответственных и днях рождениях будет удалена!\n'
                                  'Введите "Подтверждаю", чтобы отключить напоминание\n'
                                  'Введите любое другое сообщение, чтобы отменить')
    await state.set_state(ReminderOff.confirming)


@adminRouter.message(ReminderOff.confirming)
async def reminder_off_confirming(message: Message, state: FSMContext):
    if message.text.strip().lower() == 'подтверждаю':
        con = sqlite3.connect('chats.db')
        cur = con.cursor()
        con.execute('PRAGMA foreign_keys = ON')
        try:
            cur.execute(f'DELETE FROM chats WHERE id = {message.chat.id}')
            con.commit()
            refresh_responsibles()
            await message.answer('Напоминание выключено!')
        except sqlite3.Error as er:
            await message.answer('Не удалось выключить напоминание!')
        cur.close()
        con.close()
    await state.clear()


# Редактировать напоминание
@adminRouter.callback_query(F.data == 'responsible_add')
async def responsible_add(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите имя пользователя нового ответственного', reply_markup=kb.cancel)
    await callback.answer('')
    await state.set_state(NewResponsible.responsible)


@adminRouter.callback_query(NewResponsible.responsible, F.data == 'cancel')
async def cancel_responsible(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer('Отмена назначения ответственного')
    await callback.message.delete()


# Установка нового ответственного
@adminRouter.message(NewResponsible.responsible)
async def set_responsible(message: Message, state: FSMContext):
    responsible = message.text.strip()
    await state.update_data(responsible=responsible)
    await state.set_state(NewResponsible.confirm)
    await message.answer(f'Сделать ответственным @{responsible}?', reply_markup=kb.confirm)


@adminRouter.callback_query(NewResponsible.confirm, F.data == 'confirm_yes')
async def confirmed(callback: CallbackQuery, state: FSMContext):
    con = sqlite3.connect('chats.db')
    cur = con.cursor()
    con.execute('PRAGMA foreign_keys = ON')
    data = await state.get_data()
    responsible = data["responsible"]
    chat_id = callback.message.chat.id
    cur.execute(f'SELECT * FROM responsibles WHERE username = "{responsible}" AND chat_id = {chat_id}')
    rows = cur.fetchall()
    if len(rows) == 0:
        try:
            cur.execute(f'INSERT INTO responsibles (username, chat_id) VALUES ("{responsible}", {chat_id})')
            con.commit()
            refresh_responsibles()
            await callback.message.answer(f'Ответственным назначен @{responsible}')
            await callback.answer('Ответственный назначен')
        except sqlite3.Error:
            await callback.message.answer('Не удалось добавить ответственного\nПопробуйте включить напоминание')
            await callback.answer('')
    else:
        await callback.message.answer('Этот пользователь уже назначен ответственным в этом чате')
        await callback.answer('')
    cur.close()
    con.close()
    await state.clear()
    await callback.message.delete()


# эту функцию можно совместить с responsible_add
@adminRouter.callback_query(NewResponsible.confirm, F.data == 'confirm_no')
async def reminder_change(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Отмена назначения ответственного')
    await callback.answer('')
    await state.clear()
    await callback.message.delete()


@adminRouter.callback_query(F.data == 'responsible_remove')
async def responsible_remove(callback: CallbackQuery, state: FSMContext):
    con = sqlite3.connect('chats.db')
    cur = con.cursor()
    con.execute('PRAGMA foreign_keys = ON')
    chat_id = callback.message.chat.id
    cur.execute(f'SELECT username FROM responsibles JOIN chats ON responsibles.chat_id=chats.id WHERE responsibles.chat_id={chat_id}')
    responsibles = cur.fetchall()
    if len(responsibles) == 0:
        await callback.message.answer('Вы ещё не назначили ответственных, либо напоминание не включено.')
        await callback.answer('')
    else:
        resps_kb = list(map(lambda resp: [kb.KeyboardButton(text=f'{resp[0]}')], responsibles))
        resps = kb.ReplyKeyboardMarkup(keyboard=resps_kb, resize_keyboard=True, one_time_keyboard=True)
        await state.set_state(RemovingResponsible.responsible)
        await callback.message.answer('Выберите пользователя', reply_markup=resps)
        await callback.answer('')


@adminRouter.message(RemovingResponsible.responsible)
async def responsible_remove_confirm(message: Message, state: FSMContext):
    await message.answer(f'Убрать из ответственных {message.text}?', reply_markup=kb.confirm)
    await state.update_data(remove=message.text)
    await state.set_state(RemovingResponsible.confirm)


@adminRouter.callback_query(RemovingResponsible.confirm, F.data == 'confirm_yes')
async def responsible_remove_apply(callback: CallbackQuery, state: FSMContext):
    con = sqlite3.connect('chats.db')
    cur = con.cursor()
    con.execute('PRAGMA foreign_keys = ON')
    data = await state.get_data()
    responsible = data["remove"]
    chat_id = callback.message.chat.id
    try:
        cur.execute(f'DELETE FROM responsibles WHERE username = "{responsible}" AND chat_id = {chat_id}')
        con.commit()
        refresh_responsibles()
        await callback.message.answer(f'@{responsible} удалён из ответственных', reply_markup=kb.ReplyKeyboardRemove())
        await callback.answer('Ответственный удалён')
    except sqlite3.Error:
        await callback.message.answer('Не удалось удалить ответственного')
        await callback.answer('')
    cur.close()
    con.close()
    await state.clear()
    await callback.message.delete()


@adminRouter.callback_query(RemovingResponsible.confirm, F.data == 'confirm_no')
async def responsible_remove_declined(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Отмена удаления ответственного', reply_markup=kb.ReplyKeyboardRemove())
    await callback.answer('')
    await state.clear()
    await callback.message.delete()


@adminRouter.callback_query(F.data == 'table_change')
async def table_change(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TableEditing.table)
    await callback.message.answer('Введите ссылку на новую таблицу\nВведите "Удалить", чтобы удалить ссылку', reply_markup=kb.cancel)
    await callback.answer()


@adminRouter.callback_query(TableEditing.table, F.data == 'cancel')
async def table_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Отмена изменения таблицы')
    await state.clear()
    await callback.message.delete()


@adminRouter.message(TableEditing.table, F.text.strip().lower() == 'удалить')
async def table_delete(message: Message, state: FSMContext):
    con = sqlite3.connect('chats.db')
    cur = con.cursor()
    chat_id = message.chat.id
    try:
        cur.execute(f'UPDATE chats SET spreadsheet = null where id = {chat_id}')
        con.commit()
        await message.answer('Ссылка на таблицу удалена!')
    except sqlite3.Error:
        await message.answer('Не удалось удалить ссылку на таблицу')
    cur.close()
    con.close()
    await state.clear()


@adminRouter.message(TableEditing.table)
async def table_apply(message: Message, state: FSMContext):
    con = sqlite3.connect('chats.db')
    cur = con.cursor()
    new_table = message.text.strip()
    chat_id = message.chat.id
    try:
        cur.execute(f'UPDATE chats SET spreadsheet = "{new_table}" where id = {chat_id}')
        con.commit()
        await message.answer(f'Ссылка на таблицу обновлена!')
    except sqlite3.Error:
        await message.answer('Не удалось обновить ссылку на таблицу')
    cur.close()
    con.close()
    await state.clear()


# Бригада вышла
@respRouter.callback_query(F.data == 'brigade_ok')
async def brigade_ok(callback: CallbackQuery):
    await callback.message.reply('@realcaaap Бригада вышла на работу✅')
    await callback.answer('✅')


# Бригада не вышла
@respRouter.callback_query(F.data == 'brigade_fail')
async def brigade_fail(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BrigadeReason.reason)
    await state.update_data(brigade_state='Бригада НЕ вышла на работу❌')
    await callback.message.answer('Укажите причину в своём следующем сообщении')
    await callback.answer('')


# бригада вышла не в полном составе
@respRouter.callback_query(F.data == 'brigade_part')
async def brigade_part(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BrigadeReason.reason)
    await state.update_data(brigade_state='Бригада вышла на работу в неполном составе⚠️')
    await callback.message.answer('Укажите причину в своём следующем сообщении')
    await callback.answer('')


@respRouter.message(BrigadeReason.reason)
async def brigade_reason(message: Message, state: FSMContext):
    data = await state.get_data()
    brigade_state = data["brigade_state"]
    await message.reply(f'@realcaaap\n{brigade_state}')
    await state.clear()

import csv
import os.path

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import sqlite3

import app.keyboards as kb
from app.scheduler import add_brigade_planning_reminder
from app.utils.queries import execute_query
from app.utils.states import (NewResponsible, RemovingResponsible, BrigadePartly, BrigadeFail,
                              TableEditing, ReminderOff, ChangeBDays)
from app.utils.filters import (AdminCallbackFilter, AdminMessageFilter,
                               RespCallbackFilter, RespMessageFilter,
                               NewWorkCallbackFilter)
from app.utils.utils import (set_brigade_answer, set_table_answer, set_new_work_answer,
                             check_reminder_is_on, get_responsible)


adminRouter = Router()
adminRouter.callback_query.filter(AdminCallbackFilter())
adminRouter.message.filter(AdminMessageFilter())

respRouter = Router()
respRouter.callback_query.filter(RespCallbackFilter())
respRouter.message.filter(RespMessageFilter())

newWorkRouter = Router()
newWorkRouter.callback_query.filter(NewWorkCallbackFilter())

controller = '@SvetlanaD007'


# запуск бота
@adminRouter.message(Command('start'))
async def start(message: Message):
    await message.answer('Приветствую! Я буду помогать вам в процессе работы!')


# Меню напоминания
@adminRouter.message(Command('reminder'))
async def reminder(message: Message):
    await message.answer('Что нужно сделать с напоминанием?', reply_markup=kb.reminder)


@respRouter.message(Command('brigadeok'))
async def brigadeok(message: Message):
    await message.answer(f'{controller} Бригады вышли на работу✅')


@adminRouter.message(Command('birthday'))
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


@adminRouter.callback_query(F.data == 'bdays_not_changed')
async def birthday_nochanges(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Дни рождения остались без изменений')
    await state.clear()


# Включить напоминание
@adminRouter.callback_query(F.data == 'reminder_on')
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
@adminRouter.callback_query(F.data == 'reminder_off')
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


@adminRouter.callback_query(ReminderOff.confirming, F.data == 'cancel')
async def reminder_off_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('⚠️Напоминание НЕ было выключено⚠️', reply_markup=kb.reminder)
    await callback.answer('')
    await state.clear()


@adminRouter.message(ReminderOff.confirming)
async def reminder_off_confirming(message: Message, state: FSMContext):
    if message.text.strip().lower() == 'подтверждаю':
        try:
            execute_query(f'DELETE FROM chats WHERE id = {message.chat.id}')
            await message.answer('Напоминание выключено!')
        except sqlite3.Error:
            await message.answer('Не удалось выключить напоминание!')
    await state.clear()


# Редактировать напоминание
@adminRouter.callback_query(F.data == 'responsible_add')
async def responsible_add(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    if check_reminder_is_on(chat_id):
        await callback.message.edit_text('Введите имя пользователя нового ответственного (без @)', reply_markup=kb.cancel)
        await callback.answer('')
        await state.set_state(NewResponsible.responsible)
    else:
        await callback.message.edit_text('⚠️Включите напоминание, чтобы добавить ответственного⚠️', reply_markup=kb.reminder)
        await callback.answer('')


@adminRouter.callback_query(NewResponsible.responsible, F.data == 'cancel')
async def cancel_responsible(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('⚠️Отмена назначения ответственного⚠️', reply_markup=kb.reminder)
    await callback.answer('Отмена')
    await state.clear()


# Установка нового ответственного
@adminRouter.message(NewResponsible.responsible)
async def set_responsible(message: Message, state: FSMContext):
    responsible = message.text.strip()
    await state.update_data(responsible=responsible)
    await state.set_state(NewResponsible.confirm)
    await message.answer(f'Сделать ответственным @{responsible}?', reply_markup=kb.confirm)


@adminRouter.callback_query(NewResponsible.confirm, F.data == 'confirm_yes')
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
@adminRouter.callback_query(NewResponsible.confirm, F.data == 'confirm_no')
async def reminder_change(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('⚠️Отмена назначения ответственного⚠️', reply_markup=kb.reminder)
    await callback.answer('')
    await state.clear()


@adminRouter.callback_query(F.data == 'responsible_remove')
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


@adminRouter.callback_query(RemovingResponsible.responsible)
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


@adminRouter.callback_query(RemovingResponsible.confirm, F.data == 'confirm_yes')
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


@adminRouter.callback_query(RemovingResponsible.confirm, F.data == 'confirm_no')
async def responsible_remove_declined(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('⚠️Отмена удаления ответственного⚠️', reply_markup=kb.reminder)
    await callback.answer('')
    await state.clear()


@adminRouter.callback_query(F.data == 'table_change')
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


@adminRouter.callback_query(TableEditing.table, F.data == 'cancel_table')
async def table_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('⚠️Отмена изменения таблицы⚠️', reply_markup=kb.reminder)
    await callback.answer('Отмена')
    await state.clear()


@adminRouter.callback_query(TableEditing.table, F.data == 'delete_table')
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


@adminRouter.message(TableEditing.table)
async def table_apply(message: Message, state: FSMContext):
    new_table = message.text.strip()
    chat_id = message.chat.id
    try:
        execute_query(f'UPDATE chats SET spreadsheet = "{new_table}" where id = {chat_id}')
        await message.answer('✅Ссылка на таблицу обновлена✅', reply_markup=kb.reminder)
    except sqlite3.Error:
        await message.answer('❌Не удалось обновить ссылку на таблицу❌')
    await state.clear()


# Бригада вышла
@respRouter.callback_query(F.data == 'brigade_ok')
async def brigade_ok(callback: CallbackQuery):
    await callback.message.edit_text(f'{controller}\nБригады вышли на работу✅')
    await callback.answer('✅')
    set_brigade_answer(callback.message.chat.id)


# Бригады не вышли -> укажите причину
@respRouter.callback_query(F.data == 'brigade_fail')
async def brigade_fail(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Укажите бригаду(ы) и причину(ы) невыхода.')
    await callback.answer('')
    set_brigade_answer(callback.message.chat.id)
    await state.set_state(BrigadeFail.reason)


# Получена причина -> планируют ли выходить?
@respRouter.message(BrigadeFail.reason)
async def brigade_fail_reason(message: Message, state: FSMContext):
    await state.update_data(brigade_reason=message.text)
    await message.answer('Планируют ли бригады выходить сегодня?', reply_markup=kb.confirm)
    await state.set_state(BrigadeFail.planning)


# Планируют выходить -> укажите дату
@respRouter.callback_query(BrigadeFail.planning, F.data == 'confirm_yes')
async def brigade_fail_planning(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Укажите время выхода бригад.')
    await callback.answer('')
    await state.set_state(BrigadeFail.planning_date)


# Указана дата выхода -> сообщение Светлане
@respRouter.message(BrigadeFail.planning_date)
async def brigade_fail_planning_date(message: Message, state: FSMContext):
    data = await state.get_data()
    brigade_reason = data['brigade_reason']
    await message.answer(f'{controller}\n'
                         f'Бригады НЕ вышли на объект❌\n\n'
                         f'Причина:\n'
                         f'{brigade_reason}\n\n'
                         f'Дата выхода:\n'
                         f'{message.text}')
    await state.clear()


# Не планируют выходить -> укажите причину
@respRouter.callback_query(BrigadeFail.planning, F.data == 'confirm_no')
async def brigade_fail_not_planning(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Укажите причину, почему не планируют выходить.')
    await callback.answer('')
    await state.set_state(BrigadeFail.not_planning_reason)


# Получена причина -> укажите дальнейшие действия
@respRouter.message(BrigadeFail.not_planning_reason)
async def brigade_fail_not_planning_reason(message: Message, state: FSMContext):
    await state.update_data(brigade_not_planning_reason=message.text)
    await message.answer('Ваши дальнейшие действия по решению проблемы?')
    await state.set_state(BrigadeFail.further_actions)


# Получены дальнейшие действия -> сообщение Светлане
@respRouter.message(BrigadeFail.further_actions)
async def brigade_fail_further_actions(message: Message, state: FSMContext):
    data = await state.get_data()
    brigade_reason = data['brigade_reason']
    brigade_not_planning_reason = data['brigade_not_planning_reason']
    await message.answer(f'{controller}\n'
                         f'Бригады НЕ вышли на объект❌\n\n'
                         f'Бригады и причины:\n'
                         f'{brigade_reason}\n\n'
                         f'Не планируют выходить:\n'
                         f'{brigade_not_planning_reason}\n\n'
                         f'Дальнейшие действия:\n'
                         f'{message.text}')
    await state.clear()


# В неполном составе -> укажите бригады и причины
@respRouter.callback_query(F.data == 'brigade_part')
async def brigade_partly(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Укажите бригаду(ы) и причину(ы) выхода в неполном составе.')
    await callback.answer('')
    set_brigade_answer(callback.message.chat.id)
    await state.set_state(BrigadePartly.reason)


# Получена причина -> планируют ли выходить сегодня?
@respRouter.message(BrigadePartly.reason)
async def brigade_partly_reason(message: Message, state: FSMContext):
    await state.update_data(brigade_reason=message.text)
    await message.answer('Планирует(ют) ли бригада(ы) выходить сегодня?', reply_markup=kb.confirm)
    await state.set_state(BrigadePartly.coming)


# Не планируют выходить -> ваши дальнейшие действия?
@respRouter.callback_query(BrigadePartly.coming, F.data == 'confirm_no')
async def brigade_partly_not_coming(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Ваши дальнейшие действия по решению проблемы?')
    await state.set_state(BrigadePartly.further_actions)


# Дальнейшие действия -> сообщение Светлане
@respRouter.message(BrigadePartly.further_actions)
async def brigade_partly_further_actions(message: Message, state: FSMContext):
    data = await state.get_data()
    brigade_reason = data['brigade_reason']
    await message.answer(f'{controller}\n'
                         f'Бригада(ы) вышла(и) на объект в неполном составе⚠️\n'
                         f'Сегодня на объект не выйдут\n\n'
                         f'Бригады и причины:\n'
                         f'{brigade_reason}\n\n'
                         f'Дальнейшие действия:\n'
                         f'{message.text}')
    await state.clear()


# Планируют выходить -> когда?
@respRouter.callback_query(BrigadePartly.coming, F.data == 'confirm_yes')
async def brigade_partly_coming(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Когда бригада обещает выйти в полном составе? Укажите предполагаемое время.')
    await callback.answer('')
    await state.set_state(BrigadePartly.planning)


# Получили время выхода -> сообщение Светлане -> напоминание в 13:00
@respRouter.message(BrigadePartly.planning)
async def brigade_partly_planning(message: Message, state: FSMContext):
    data = await state.get_data()
    brigade_reason = data['brigade_reason']
    await message.answer(f'{controller}\n'
                         f'Бригада(ы) вышла(и) на объект в неполном составе⚠️\n'
                         f'Выйдут на объект позже.\n\n'
                         f'Бригады и причины:\n'
                         f'{brigade_reason}\n\n'
                         f'Время выхода:\n'
                         f'{message.text}')
    await state.clear()
    add_brigade_planning_reminder(message)


@respRouter.callback_query(F.data == 'remind_later_yes')
async def remind_later_yes(callback: CallbackQuery):
    await callback.message.edit_text(f'{controller}\n'
                                     f'Рабочие вышли на объект✅')
    await callback.answer('')


@respRouter.callback_query(F.data == 'remind_later_no')
async def remind_later_yes(callback: CallbackQuery):
    await callback.message.edit_text(f'{controller}\n'
                                     f'Рабочие не вышли на объект❌')
    await callback.answer('')


@respRouter.callback_query(F.data == 'table_updated')
async def table_updated(callback: CallbackQuery):
    await callback.message.answer(f'{controller}\nТаблица обновлена!✅')
    await callback.answer('')
    set_table_answer(callback.message.chat.id)


@newWorkRouter.callback_query(F.data == 'new_work_no')
async def new_work_no(callback: CallbackQuery):
    await callback.message.edit_text(f'{controller}\n'
                                     f'Новый вид работ на объекте не планируется.')
    await callback.answer('')
    set_new_work_answer(callback.message.chat.id)


@newWorkRouter.callback_query(F.data == 'new_work_yes')
async def new_work_yes(callback: CallbackQuery):
    await callback.message.edit_text('Основные виды работ или подневщики?', reply_markup=kb.new_work_type)
    await callback.answer('')
    set_new_work_answer(callback.message.chat.id)


@newWorkRouter.callback_query(F.data == 'new_work_main')
async def new_work_main(callback: CallbackQuery):
    await callback.message.edit_text('Заполните данные согласно  форме: https://forms.gle/3mpAhFGTrQtgpWqVA')
    await callback.answer('')


@newWorkRouter.callback_query(F.data == 'new_work_daily')
async def new_work_main(callback: CallbackQuery):
    await callback.message.edit_text('Заполните данные согласно  форме: https://forms.gle/qnqkPEdiNj9gbq6C9 ')
    await callback.answer('')


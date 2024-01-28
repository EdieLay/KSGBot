from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
from app.scheduler import add_brigade_planning_reminder
from app.utils.states import BrigadePartly, BrigadeFail
from app.utils.utils import set_brigade_answer
from tokens import controller

brigadeReportRouter = Router()


# Бригада вышла
@brigadeReportRouter.callback_query(F.data == 'brigade_ok')
async def brigade_ok(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(✅Бригады вышли✅)')
    await callback.message.answer(f'{controller}\nБригады вышли на работу✅')
    await callback.answer('')
    set_brigade_answer(callback.message.chat.id)


# Бригады не вышли -> укажите причину
@brigadeReportRouter.callback_query(F.data == 'brigade_fail')
async def brigade_fail(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(callback.message.text + '\n(❌Бригады не вышли❌)')
    await callback.message.answer('Укажите бригаду(ы) и причину(ы) невыхода.')
    await callback.answer('')
    set_brigade_answer(callback.message.chat.id)
    await state.set_state(BrigadeFail.reason)


# Получена причина -> планируют ли выходить?
@brigadeReportRouter.message(BrigadeFail.reason)
async def brigade_fail_reason(message: Message, state: FSMContext):
    await state.update_data(brigade_reason=message.text)
    await message.answer('Планируют ли бригады выходить сегодня?', reply_markup=kb.confirm)
    await state.set_state(BrigadeFail.planning)


# Планируют выходить -> укажите дату
@brigadeReportRouter.callback_query(BrigadeFail.planning, F.data == 'confirm_yes')
async def brigade_fail_planning(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(callback.message.text + '\n(Да)')
    await callback.message.answer('Укажите время выхода бригад.')
    await callback.answer('')
    await state.set_state(BrigadeFail.planning_date)


# Указана дата выхода -> сообщение Светлане
@brigadeReportRouter.message(BrigadeFail.planning_date)
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
@brigadeReportRouter.callback_query(BrigadeFail.planning, F.data == 'confirm_no')
async def brigade_fail_not_planning(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(callback.message.text + '\n(Нет)')
    await callback.message.answer('Укажите причину, почему не планируют выходить.')
    await callback.answer('')
    await state.set_state(BrigadeFail.not_planning_reason)


# Получена причина -> укажите дальнейшие действия
@brigadeReportRouter.message(BrigadeFail.not_planning_reason)
async def brigade_fail_not_planning_reason(message: Message, state: FSMContext):
    await state.update_data(brigade_not_planning_reason=message.text)
    await message.answer('Ваши дальнейшие действия по решению проблемы?')
    await state.set_state(BrigadeFail.further_actions)


# Получены дальнейшие действия -> сообщение Светлане
@brigadeReportRouter.message(BrigadeFail.further_actions)
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
@brigadeReportRouter.callback_query(F.data == 'brigade_part')
async def brigade_partly(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(callback.message.text + '\n(⚠️Бригада(ы) вышла(и) в неполном составе⚠️)')
    await callback.message.answer('Укажите бригаду(ы) и причину(ы) выхода в неполном составе.')
    await callback.answer('')
    set_brigade_answer(callback.message.chat.id)
    await state.set_state(BrigadePartly.reason)


# Получена причина -> планируют ли выходить сегодня?
@brigadeReportRouter.message(BrigadePartly.reason)
async def brigade_partly_reason(message: Message, state: FSMContext):
    await state.update_data(brigade_reason=message.text)
    await message.answer('Планирует(ют) ли бригада(ы) выходить сегодня?', reply_markup=kb.confirm)
    await state.set_state(BrigadePartly.coming)


# Не планируют выходить -> ваши дальнейшие действия?
@brigadeReportRouter.callback_query(BrigadePartly.coming, F.data == 'confirm_no')
async def brigade_partly_not_coming(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(callback.message.text + '\n(Нет)')
    await callback.message.answer('Ваши дальнейшие действия по решению проблемы?')
    await callback.answer('')
    await state.set_state(BrigadePartly.further_actions)


# Дальнейшие действия -> сообщение Светлане
@brigadeReportRouter.message(BrigadePartly.further_actions)
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
@brigadeReportRouter.callback_query(BrigadePartly.coming, F.data == 'confirm_yes')
async def brigade_partly_coming(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(callback.message.text + '\n(Да)')
    await callback.message.answer('Когда бригада обещает выйти в полном составе? Укажите предполагаемое время.')
    await callback.answer('')
    await state.set_state(BrigadePartly.planning)


# Получили время выхода -> сообщение Светлане -> напоминание в 13:00
@brigadeReportRouter.message(BrigadePartly.planning)
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


@brigadeReportRouter.callback_query(F.data == 'remind_later_yes')
async def remind_later_yes(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(Да)')
    await callback.message.answer(f'{controller}\n'
                                  f'Рабочие вышли на объект✅')
    await callback.answer('')


@brigadeReportRouter.callback_query(F.data == 'remind_later_no')
async def remind_later_yes(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(Нет)')
    await callback.message.answer(f'{controller}\n'
                                  f'Рабочие не вышли на объект❌')
    await callback.answer('')
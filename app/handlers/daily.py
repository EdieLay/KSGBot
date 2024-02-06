from aiogram import F, Router
from aiogram.types import CallbackQuery

import app.keyboards as kb
from app.utils.utils import set_answer
from tokens import controller

dailyRouter = Router()


@dailyRouter.callback_query(F.data == 'morning_plan_making')
async def morning_plan_done(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(Отчёт формируется)')
    await callback.message.answer('Нажмите "ГОТОВО", когда отчёт будет готов', reply_markup=kb.morning_plan_done)
    await callback.answer('')
    set_answer(callback.message.chat.id, 'morning_plan_answered')


@dailyRouter.callback_query(F.data == 'morning_plan_done')
async def morning_plan_done(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(ГОТОВО)')
    await callback.message.reply(f'{controller}\nПлан работ и отчёт предоставлены.')
    await callback.answer('')


@dailyRouter.callback_query(F.data == 'night_payment_making')
async def night_payment_done(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(Заявка и отчёт формируются)')
    await callback.message.answer('Нажмите "ГОТОВО", когда заявка и отчёт будут готовы', reply_markup=kb.night_payment_done)
    await callback.answer('')
    set_answer(callback.message.chat.id, 'night_payment_answered')


@dailyRouter.callback_query(F.data == 'night_payment_done')
async def night_payment_done(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(ГОТОВО)')
    await callback.message.reply(f'{controller}\nЗаявка подана, фото отправлены.')
    await callback.answer('')


@dailyRouter.callback_query(F.data == 'night_payment_not')
async def night_payment_done(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(Ночной смены не было)')
    await callback.message.reply(f'{controller}\nНочной смены не было.')
    await callback.answer('')
    set_answer(callback.message.chat.id, 'night_payment_answered')


@dailyRouter.callback_query(F.data == 'day_payment_making')
async def day_payment_done(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(Заявка формируется)')
    await callback.message.answer('Нажмите "ГОТОВО", когда заявка будет готова', reply_markup=kb.day_payment_done)
    await callback.answer('')
    set_answer(callback.message.chat.id, 'day_payment_answered')


@dailyRouter.callback_query(F.data == 'day_payment_done')
async def day_payment_done(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(ГОТОВО)')
    await callback.message.reply(f'{controller}\nЗаявка подана.')
    await callback.answer('')


@dailyRouter.callback_query(F.data == 'day_payment_not')
async def day_payment_not(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(Дневной смены не было)')
    await callback.message.reply(f'{controller}\nДневной смены не было сегодня.')
    await callback.answer('')
    set_answer(callback.message.chat.id, 'day_payment_answered')


@dailyRouter.callback_query(F.data == 'evening_plan_making')
async def evening_plan_done(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(Заявка и отчёт формируются)')
    await callback.message.answer('Нажмите "ГОТОВО", когда заявка будет готова', reply_markup=kb.evening_plan_done)
    await callback.answer('')
    set_answer(callback.message.chat.id, 'evening_plan_answered')


@dailyRouter.callback_query(F.data == 'evening_plan_done')
async def evening_plan_done(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(ГОТОВО)')
    await callback.message.reply(f'{controller}\nПлан работ, отчет и заявка на оплату за сегодня предоставлены.')
    await callback.answer('')


@dailyRouter.callback_query(F.data == 'evening_plan_tomorrow')
async def evening_plan_done(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(Отчёт и заявка будут поданы завтра)')
    await callback.message.reply(f'{controller}\nОтчёт и заявка будут поданы завтра.')
    await callback.answer('')
    set_answer(callback.message.chat.id, 'evening_plan_answered')


@dailyRouter.callback_query(F.data == 'tomorrow_plan_making')
async def tomorrow_plan_done(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(Заявка и отчёт формируются)')
    await callback.message.answer('Нажмите "ГОТОВО", когда заявка будет готова', reply_markup=kb.tomorrow_plan_done)
    await callback.answer('')
    set_answer(callback.message.chat.id, 'tomorrow_plan_answered')


@dailyRouter.callback_query(F.data == 'tomorrow_plan_done')
async def tomorrow_plan_done(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(ГОТОВО)')
    await callback.message.reply(f'{controller}\nПлан работ на завтра предоставлен.')
    await callback.answer('')


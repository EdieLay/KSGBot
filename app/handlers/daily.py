from aiogram import F, Router
from aiogram.types import CallbackQuery

import app.keyboards as kb
from app.utils.utils import set_answer
from tokens import controller

dailyRouter = Router()


@dailyRouter.callback_query(F.data == 'morning_plan_done')
async def morning_plan_done(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(ГОТОВО)')
    await callback.message.reply(f'{controller}\nПлан работ и фото предоставлены.')
    await callback.answer('')
    set_answer(callback.message.chat.id, 'morning_plan_answered')


@dailyRouter.callback_query(F.data == 'night_payment_done')
async def night_payment_done(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(ГОТОВО)')
    await callback.message.reply(f'{controller}\nЗаявка подана, фото отправлены.')
    await callback.answer('')
    set_answer(callback.message.chat.id, 'night_payment_answered')


@dailyRouter.callback_query(F.data == 'day_payment_done')
async def day_payment_done(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(ГОТОВО)')
    await callback.message.reply(f'{controller}\nЗаявка подана.')
    await callback.answer('')
    set_answer(callback.message.chat.id, 'day_payment_answered')


@dailyRouter.callback_query(F.data == 'day_payment_not')
async def day_payment_not(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(Дневной смены не было)')
    await callback.message.reply(f'{controller}\nДневной смены не было сегодня.')
    await callback.answer('')
    set_answer(callback.message.chat.id, 'day_payment_answered')


@dailyRouter.callback_query(F.data == 'tomorrow_plan_done')
async def tomorrow_plan_done(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(ГОТОВО)')
    await callback.message.reply(f'{controller}\nПлан работ на завтра предоставлен.')
    await callback.answer('')
    set_answer(callback.message.chat.id, 'tomorrow_plan_answered')


@dailyRouter.callback_query(F.data == 'evening_plan_done')
async def evening_plan_done(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(ГОТОВО)')
    await callback.message.reply(f'{controller}\nПлан работ, отчет и заявка на оплату за сегодня предоставлены.')
    await callback.answer('')
    set_answer(callback.message.chat.id, 'evening_plan_answered')




from aiogram import F, Router
from aiogram.types import CallbackQuery

import app.keyboards as kb
from app.utils.utils import set_answer
from tokens import controller

weeklyRouter = Router()


@weeklyRouter.callback_query(F.data == 'table_updated')
async def table_updated(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(Таблица обновлена)')
    await callback.message.answer(f'{controller}\nТаблица обновлена!✅')
    await callback.answer('')
    set_answer(callback.message.chat.id, 'table_answered')


@weeklyRouter.callback_query(F.data == 'new_work_no')
async def new_work_no(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(Нет)')
    await callback.message.answer(f'{controller}\n'
                                  f'Новые работники не нужны.')
    await callback.answer('')
    set_answer(callback.message.chat.id, 'new_work_answered')


@weeklyRouter.callback_query(F.data == 'new_work_yes')
async def new_work_yes(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(Да)')
    await callback.message.answer('Будут начаты работы по контракту или нужны разнорабочие?', reply_markup=kb.new_work_type)
    await callback.answer('')
    set_answer(callback.message.chat.id, 'new_work_answered')


@weeklyRouter.callback_query(F.data == 'new_work_main')
async def new_work_main(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(Работы по контракту)')
    await callback.message.answer('Заполните данные согласно  форме: https://forms.gle/3mpAhFGTrQtgpWqVA')
    await callback.answer('')


@weeklyRouter.callback_query(F.data == 'new_work_daily')
async def new_work_main(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + '\n(Разнорабочие)')
    await callback.message.answer('Заполните данные согласно  форме: https://forms.gle/qnqkPEdiNj9gbq6C9 ')
    await callback.answer('')
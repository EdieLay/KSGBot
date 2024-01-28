from aiogram import F, Router
from aiogram.types import CallbackQuery

import app.keyboards as kb
from app.utils.utils import set_table_answer, set_new_work_answer
from tokens import controller

dailyRouter = Router()



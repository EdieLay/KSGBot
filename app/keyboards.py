from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

# клавиатура подтверждения выход бригады
brigade_report_kb = [
    [InlineKeyboardButton(text='✅Бригада вышла✅', callback_data='brigade_ok')],
    [InlineKeyboardButton(text='❌Бригада не вышла❌', callback_data='brigade_fail')],
    [InlineKeyboardButton(text='❌✅Бригада вышла не в полном составе✅❌', callback_data='brigade_part')]
]

brigade_report = InlineKeyboardMarkup(inline_keyboard=brigade_report_kb)

reminder_kb = [
    [InlineKeyboardButton(text='Включить напоминание', callback_data='reminder_on'),
     InlineKeyboardButton(text='Отключить напоминание', callback_data='reminder_off')],
    [InlineKeyboardButton(text='Добавить ответственного', callback_data='reminder_add'),
     InlineKeyboardButton(text='Удалить ответственного', callback_data='reminder_remove')]
]

reminder = InlineKeyboardMarkup(inline_keyboard=reminder_kb)

confirm_kb = [
    [InlineKeyboardButton(text='Да', callback_data='confirm_yes')],
    [InlineKeyboardButton(text='Нет', callback_data='confirm_no')]
]

confirm = InlineKeyboardMarkup(inline_keyboard=confirm_kb)

cancel_responsible = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отменить', callback_data='cancel_responsible')]
])
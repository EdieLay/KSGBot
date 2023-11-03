from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove


# клавиатура подтверждения выхода бригады
brigade_report_kb = [
    [InlineKeyboardButton(text='✅Бригада вышла✅', callback_data='brigade_ok')],
    [InlineKeyboardButton(text='⚠️Бригада вышла не в полном составе⚠️', callback_data='brigade_part')],
    [InlineKeyboardButton(text='❌Бригада не вышла❌', callback_data='brigade_fail')]
]
brigade_report = InlineKeyboardMarkup(inline_keyboard=brigade_report_kb)

reminder_kb = [
    [InlineKeyboardButton(text='Включить напоминание', callback_data='reminder_on'),
     InlineKeyboardButton(text='Отключить напоминание', callback_data='reminder_off')],
    [InlineKeyboardButton(text='Добавить ответственного', callback_data='responsible_add'),
     InlineKeyboardButton(text='Удалить ответственного', callback_data='responsible_remove')],
    [InlineKeyboardButton(text='Изменить ссылку на таблицу', callback_data='table_change')]
]
reminder = InlineKeyboardMarkup(inline_keyboard=reminder_kb)

confirm_kb = [
    [InlineKeyboardButton(text='Да', callback_data='confirm_yes')],
    [InlineKeyboardButton(text='Нет', callback_data='confirm_no')]
]
confirm = InlineKeyboardMarkup(inline_keyboard=confirm_kb)

cancel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отменить', callback_data='cancel')]
])

change_bdays = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Без изменений', callback_data='change_bdays')]
])

cancel_table = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отменить', callback_data='cancel_table'),
     InlineKeyboardButton(text='Удалить', callback_data='delete_table')]
])
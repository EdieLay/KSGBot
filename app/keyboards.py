from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

morning_plan_making_kb = [[InlineKeyboardButton(text='Отчёт формируется', callback_data='morning_plan_making')]]
morning_plan_making = InlineKeyboardMarkup(inline_keyboard=morning_plan_making_kb)
morning_plan_done_kb = [[InlineKeyboardButton(text='ГОТОВО', callback_data='morning_plan_done')]]
morning_plan_done = InlineKeyboardMarkup(inline_keyboard=morning_plan_done_kb)

# клавиатура подтверждения выхода бригады
brigade_report_kb = [
    [InlineKeyboardButton(text='✅Бригады вышли✅', callback_data='brigade_ok')],
    [InlineKeyboardButton(text='⚠️Бригада(ы) вышла(и) в неполном составе⚠️', callback_data='brigade_part')],
    [InlineKeyboardButton(text='❌Бригады не вышли❌', callback_data='brigade_fail')]
]
brigade_report = InlineKeyboardMarkup(inline_keyboard=brigade_report_kb)

night_payment_making_kb = [[InlineKeyboardButton(text='Заявка и отчёт формируются', callback_data='night_payment_making')],
                           [InlineKeyboardButton(text='Ночной смены не было', callback_data='night_payment_not')]]
night_payment_making = InlineKeyboardMarkup(inline_keyboard=night_payment_making_kb)
night_payment_done_kb = [[InlineKeyboardButton(text='ГОТОВО', callback_data='night_payment_done')]]
night_payment_done = InlineKeyboardMarkup(inline_keyboard=night_payment_done_kb)

day_payment_making_kb = [[InlineKeyboardButton(text='Заявка формируется', callback_data='day_payment_making')],
                  [InlineKeyboardButton(text='Дневной смены не было', callback_data='day_payment_not')]]
day_payment_making = InlineKeyboardMarkup(inline_keyboard=day_payment_making_kb)
day_payment_done_kb = [[InlineKeyboardButton(text='ГОТОВО', callback_data='day_payment_done')]]
day_payment_done = InlineKeyboardMarkup(inline_keyboard=day_payment_done_kb)

evening_plan_making_kb = [[InlineKeyboardButton(text='Заявка и отчёт формируются', callback_data='evening_plan_making')],
                          [InlineKeyboardButton(text='Отчёт и заявка будут поданы завтра', callback_data='evening_plan_tomorrow')]]
evening_plan_making = InlineKeyboardMarkup(inline_keyboard=evening_plan_making_kb)
evening_plan_done_kb = [[InlineKeyboardButton(text='ГОТОВО', callback_data='evening_plan_done')]]
evening_plan_done = InlineKeyboardMarkup(inline_keyboard=evening_plan_done_kb)

tomorrow_plan_making_kb = [[InlineKeyboardButton(text='Заявка и отчёт формируются', callback_data='tomorrow_plan_making')],]
tomorrow_plan_making = InlineKeyboardMarkup(inline_keyboard=tomorrow_plan_making_kb)
tomorrow_plan_done_kb = [[InlineKeyboardButton(text='ГОТОВО', callback_data='tomorrow_plan_done')]]
tomorrow_plan_done = InlineKeyboardMarkup(inline_keyboard=tomorrow_plan_done_kb)

reminder_kb = [
    [InlineKeyboardButton(text='Включить напоминание', callback_data='reminder_on'),
     InlineKeyboardButton(text='Отключить напоминание', callback_data='reminder_off')],
    [InlineKeyboardButton(text='Добавить ответственного', callback_data='responsible_add'),
     InlineKeyboardButton(text='Удалить ответственного', callback_data='responsible_remove')],
    [InlineKeyboardButton(text='Добавить рук.строя', callback_data='construction_manager_add'),
     InlineKeyboardButton(text='Удалить рук.строя', callback_data='construction_manager_remove')],
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
    [InlineKeyboardButton(text='Без изменений', callback_data='bdays_not_changed')]
])

cancel_table = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отменить', callback_data='cancel_table'),
     InlineKeyboardButton(text='Удалить таблицу', callback_data='delete_table')]
])

table_reminder = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Таблица обновлена', callback_data='table_updated')]
])

remind_later = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='remind_later_yes'),
     InlineKeyboardButton(text='Нет', callback_data='remind_later_no')]
])

new_work = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='new_work_yes'),
     InlineKeyboardButton(text='Нет', callback_data='new_work_no')]
])

new_work_type = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Работы по контракту', callback_data='new_work_main')],
    [InlineKeyboardButton(text='Разнорабочие', callback_data='new_work_daily')]
])

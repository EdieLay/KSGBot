from aiogram.fsm.state import State, StatesGroup


class NewResponsible(StatesGroup):
    responsible = State()
    confirm = State()


class RemovingResponsible(StatesGroup):
    responsible = State()
    confirm = State()


class BrigadeReason(StatesGroup):
    will_come = State()
    reason = State()
    partly_reason = State()


class TableEditing(StatesGroup):
    table = State()


class ReminderOff(StatesGroup):
    confirming = State()


class ChangeBDays(StatesGroup):
    change = State()
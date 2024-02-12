from aiogram.fsm.state import State, StatesGroup


class NewResponsible(StatesGroup):
    responsible = State()
    confirm = State()


class RemovingResponsible(StatesGroup):
    responsible = State()
    confirm = State()


class NewConstructionManager(StatesGroup):
    manager = State()
    confirm = State()


class RemovingConstructionManager(StatesGroup):
    manager = State()
    confirm = State()


class BrigadePartly(StatesGroup):
    reason = State()
    coming = State()
    further_actions = State()
    planning = State()


class BrigadeFail(StatesGroup):
    reason = State()
    planning = State()
    planning_date = State()
    not_planning_reason = State()
    further_actions = State()


class TableEditing(StatesGroup):
    table = State()


class RequestsTableEditing(StatesGroup):
    table = State()


class ReminderOff(StatesGroup):
    confirming = State()


class ChangeBDays(StatesGroup):
    change = State()
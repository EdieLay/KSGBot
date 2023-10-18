from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


class NewResponsible(StatesGroup):
    responsible = State()
    confirm = State()


class RemovingResponsible(StatesGroup):
    responsible = State()
    confirm = State()


class BrigadeReason(StatesGroup):
    reason = State()


class CallbackAdminFilter(BaseFilter):
    def __init__(self):
        super()

    async def __call__(self, callback: CallbackQuery) -> bool:
        return await is_admin(callback.message)


class MessageAdminFilter(BaseFilter):
    def __init__(self):
        super()

    async def __call__(self, message: Message) -> bool:
        return await is_admin(message)


async def is_admin(message: Message):
    id = message.from_user.id
    admins = await message.chat.get_administrators()
    ids = list(map(lambda admin: admin.user.id, admins))
    return id in ids
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from app.utils.utils import is_admin, get_responsible


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


class CallbackRespFilter(BaseFilter):
    def __init__(self):
        super()

    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.from_user.username in get_responsible(callback.message.chat.id)


class MessageRespFilter(BaseFilter):
    def __init__(self):
        super()

    async def __call__(self, message: Message) -> bool:
        return message.from_user.username in get_responsible(message.chat.id)
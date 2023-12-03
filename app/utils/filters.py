from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from app.utils.utils import is_admin, get_responsible


class AdminCallbackFilter(BaseFilter):
    def __init__(self):
        super()

    async def __call__(self, callback: CallbackQuery) -> bool:
        return await is_admin(callback.message)


class AdminMessageFilter(BaseFilter):
    def __init__(self):
        super()

    async def __call__(self, message: Message) -> bool:
        return await is_admin(message)


class RespCallbackFilter(BaseFilter):
    def __init__(self):
        super()

    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.from_user.username in get_responsible(callback.message.chat.id)


class RespMessageFilter(BaseFilter):
    def __init__(self):
        super()

    async def __call__(self, message: Message) -> bool:
        return message.from_user.username in get_responsible(message.chat.id)


class NewWorkCallbackFilter(BaseFilter):
    def __init__(self):
        super()

    async def __call__(self, callback: CallbackQuery) -> bool:
        resp = get_responsible(callback.message.chat.id)
        resp.append('KonstantinSoleniy')
        return callback.from_user.username in resp


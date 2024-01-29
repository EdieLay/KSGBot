from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from app.utils.utils import is_admin, get_responsible, get_construction_managers


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
        username = callback.from_user.username
        chat_id = callback.message.chat.id
        resp = get_responsible(chat_id)
        managers = get_construction_managers(chat_id)
        return username in resp or username in managers


class RespMessageFilter(BaseFilter):
    def __init__(self):
        super()

    async def __call__(self, message: Message) -> bool:
        username = message.from_user.username
        chat_id = message.chat.id
        resp = get_responsible(chat_id)
        managers = get_construction_managers(chat_id)
        return username in resp or username in managers


class NewWorkCallbackFilter(BaseFilter):
    def __init__(self):
        super()

    async def __call__(self, callback: CallbackQuery) -> bool:
        resp = get_responsible(callback.message.chat.id)
        resp.append('KonstantinSoleniy')
        return callback.from_user.username in resp


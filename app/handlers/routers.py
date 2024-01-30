from aiogram import Router

from app.handlers.commands import commandsRouter
from app.handlers.weekly import weeklyRouter
from app.handlers.daily import dailyRouter
from app.handlers.brigadeReport import brigadeReportRouter
from app.utils.filters import (AdminCallbackFilter, AdminMessageFilter,
                               RespCallbackFilter, RespMessageFilter)

adminRouter = Router()
adminRouter.callback_query.filter(AdminCallbackFilter())
adminRouter.message.filter(AdminMessageFilter())
adminRouter.include_routers(commandsRouter)

respRouter = Router()
respRouter.callback_query.filter(RespCallbackFilter())
respRouter.message.filter(RespMessageFilter())
respRouter.include_routers(dailyRouter, weeklyRouter, brigadeReportRouter)

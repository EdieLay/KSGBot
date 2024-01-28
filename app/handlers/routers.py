from aiogram import Router

from app.handlers.commands import commandsRouter
from app.handlers.weekly import weeklyRouter
from app.handlers.brigadeReport import brigadeReportRouter
from app.utils.filters import (AdminCallbackFilter, AdminMessageFilter,
                               RespCallbackFilter, RespMessageFilter)

adminRouter = Router()
commandsRouter.callback_query.filter(AdminCallbackFilter())
commandsRouter.message.filter(AdminMessageFilter())
adminRouter.include_routers(commandsRouter)

respRouter = Router()
brigadeReportRouter.callback_query.filter(RespCallbackFilter())
brigadeReportRouter.message.filter(RespMessageFilter())
respRouter.include_routers(weeklyRouter, brigadeReportRouter)

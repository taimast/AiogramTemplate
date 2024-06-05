from aiogram import Router

from . import directed, integrated

on = Router(name="payment")
# on.include_routers(
# directed.on,
# integrated.on
# )

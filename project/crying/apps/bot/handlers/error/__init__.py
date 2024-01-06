from aiogram import Router

from . import errors

on = Router(name="error")
on.include_routers(
    errors.on,
)

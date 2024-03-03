from aiogram import Router

from . import connect

on = Router(name="connect")
on.include_routers(
    connect.on,
)

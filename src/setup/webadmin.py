import asyncio

import uvicorn
from loguru import logger
from sqladmin import Admin

from .opts import SetupOpts
from ..apps.webadmin.app import app, AdminAuth
from ..apps.webadmin.models import UserAdmin


async def setup_webadmin(opts: SetupOpts):
    wb_settings = opts.settings.webadmin
    authentication_backend = AdminAuth(secret_key=wb_settings.secret_key.get_secret_value())
    authentication_backend.password = wb_settings.password.get_secret_value()
    admin = Admin(
        app,
        session_maker=opts.session_maker,
        authentication_backend=authentication_backend
    )
    admin.add_view(UserAdmin)

    config = uvicorn.Config(app, host="127.0.0.1", port=8083, log_level="warning")
    server = uvicorn.Server(config)

    _task = asyncio.create_task(server.serve())
    logger.info("WebAdmin started")

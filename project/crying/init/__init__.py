from .commands import set_commands
from .db import init_db, close_db
from .middlewares import setup_middlewares
from .routers import setup_routers
from .scheduler import setup_scheduler
from .translator import init_translator_hub
from .webhook import start_webhook

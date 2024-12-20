from src.setup.opts import SetupOpts
from src.utils.support import SupportConnector


async def setup_support_connector(opts: SetupOpts):
    if opts.settings.support:
        return SupportConnector(opts.bot, opts.settings.support.chat_id)
    return None

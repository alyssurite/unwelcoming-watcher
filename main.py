"""Main module"""

import asyncio

# python-telegram-bot client
from bot.app.ptbclient import ptb_app

# logging
from bot.loggers import setup_logging

if __name__ == "__main__":
    setup_logging()
    asyncio.run(ptb_app.run_polling())

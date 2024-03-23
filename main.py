"""Main module"""

# python-telegram-bot client
from bot.app.ptbclient import ptb_app

# pyrogram client
from bot.app.pyroclient import pyro_app

# logging
from bot.loggers import setup_logging

if __name__ == "__main__":
    setup_logging()
    pyro_app.run(ptb_app.run_polling())

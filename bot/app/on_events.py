from telegram.ext import Application

from bot.app.pyroclient import pyro_app


async def on_bot_init(app: Application) -> None:
    await pyro_app.start()


async def on_bot_stop(app: Application) -> None:
    await pyro_app.stop()

"""App editors"""

import logging

# python-telegram-bot
from telegram import Message, Update

log = logging.getLogger(__name__)


async def edit_message(update: Update, text: str, **kwargs) -> Message:
    await update.effective_message.edit_reply_markup()
    await update.effective_message.edit_text(text)

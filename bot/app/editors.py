"""App editors"""

import logging

# python-telegram-bot
from telegram import Message, Update
from telegram.error import BadRequest

log = logging.getLogger(__name__)


async def edit_direct_message(message: Message, text: str, **kwargs) -> Message:
    try:
        await message.edit_reply_markup()
    except BadRequest:
        log.info("Edit Message: No markup.")
    return await message.edit_text(text)


async def edit_message(update: Update, text: str, **kwargs) -> Message:
    return await edit_direct_message(update.effective_message, text, **kwargs)

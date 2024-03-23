import logging

from telegram import Message, Update

log = logging.getLogger(__name__)


async def send_reply(update: Update, text: str, **kwargs) -> Message:
    await update.effective_message.reply_text(text, **kwargs)


async def send_error(update: Update, text: str, **kwargs) -> Message:
    await update.effective_message.reply_text(f"\\[ ❌ *ОШИБКА* \\] {text}", **kwargs)

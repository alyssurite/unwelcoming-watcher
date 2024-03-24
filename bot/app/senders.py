"""App senders"""

import logging

# python-telegram-bot
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.ext import ContextTypes

# app formatters
from bot.app.formatters import generate_confirmation_text

log = logging.getLogger(__name__)


async def send_reply(update: Update, text: str, **kwargs) -> Message:
    await update.effective_message.reply_text(text, **kwargs)


async def send_error(update: Update, text: str, **kwargs) -> Message:
    await update.effective_message.reply_text(f"\\[ ❌ *ОШИБКА* \\] {text}", **kwargs)


async def send_confirmation(
    update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int, **kwargs
) -> Message:
    await send_reply(
        update,
        await generate_confirmation_text(context, chat_id),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Да",
                        callback_data=f"y:{chat_id}",
                    ),
                    InlineKeyboardButton(
                        "Нет",
                        callback_data=f"n:{chat_id}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Отмена",
                        callback_data=f"c:{chat_id}",
                    ),
                ],
            ],
        ),
    )

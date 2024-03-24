"""App senders"""

import logging

from typing import Optional

# python-telegram-bot
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.ext import ContextTypes

# app formatters
from bot.app.formatters import generate_confirmation_text, generate_user_info
from bot.db.getters import get_superusers

# database getters
from .pyroclient import get_user_info

log = logging.getLogger(__name__)


async def send_reply(update: Update, text: str, **kwargs) -> Message:
    return await update.effective_message.reply_text(text, **kwargs)


async def send_error(update: Update, text: str, **kwargs) -> Message:
    return await update.effective_message.reply_text(
        f"\\[ ❌ *ОШИБКА* \\] {text}", **kwargs
    )


async def send_confirmation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    **kwargs,
) -> Message:
    return await send_reply(
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


async def send_to_superusers(context: ContextTypes.DEFAULT_TYPE, text: str, **kwargs):
    superusers = await get_superusers()
    for superuser in superusers:
        await context.bot.send_message(superuser.id, text)


async def send_info(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    user_id: int,
) -> Optional[Message]:
    log.info("They want info about %d in chat %d.", user_id, chat_id)
    if user := await get_user_info(user_id):
        user_id = user.id
        if user.id > 0:
            return await context.bot.send_message(
                chat_id,
                await generate_user_info(user),
            )
    return await context.bot.send_message(
        chat_id,
        f"ID \\[`{user_id}`\\] не принадлежит пользователю\\!",
    )

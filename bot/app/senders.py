"""App senders"""

import logging

# python-telegram-bot
from telegram import Chat, InlineKeyboardButton, InlineKeyboardMarkup, Message, Update

log = logging.getLogger(__name__)


async def send_reply(update: Update, text: str, **kwargs) -> Message:
    await update.effective_message.reply_text(text, **kwargs)


async def send_error(update: Update, text: str, **kwargs) -> Message:
    await update.effective_message.reply_text(f"\\[ ❌ *ОШИБКА* \\] {text}", **kwargs)


async def send_confirmation(update: Update, group: Chat, **kwargs) -> Message:
    await send_reply(
        update,
        "Подтверждаете действие\\?",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Да",
                        callback_data=f"y:{group.id}",
                    ),
                    InlineKeyboardButton(
                        "Нет",
                        callback_data=f"n:{group.id}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Отмена",
                        callback_data=f"c:{group.id}",
                    ),
                ],
            ],
        ),
    )

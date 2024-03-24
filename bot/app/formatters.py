"""App generatora"""

import logging

from typing import Any

# python-telegram-bot
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

# database getters
from bot.db.getters import get_users

log = logging.getLogger(__name__)


def escape_any(text: Any):
    return escape_markdown(str(text), 2)


def escape_id(some_id: int | str):
    return escape_any(some_id)


async def generate_confirmation_text(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
) -> str:
    text = ["Вы собираетесь удалить из всех чатов\\:", ""]
    users = await get_users(context.bot_data["kick"][chat_id].keys())
    for user in users:
        nick = f"@{user.username}" if user.username else ""
        text.append(f"\\[`{user.id}`\\] {escape_any(user.telegram_full_name)} {nick}")
    text.append("")
    text.append("Подтверждаете действие\\?")
    return "\n".join(text)


async def generate_report(success: set, failure: set):
    return "Успех\\."

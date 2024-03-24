"""App generatora"""

import logging

from typing import Any

# pyrogram
from pyrogram.types import User

# python-telegram-bot
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

# database getters
from bot.db.getters import get_user_groups, get_users

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


bool_to_text = {
    True: "Да",
    False: "Нет",
}


def get_full_name(user: User):
    if user.last_name:
        return f"{user.first_name} {user.last_name}"
    return user.first_name


async def generate_user_info(user: User):
    text = ["Информация о пользователе\\:", ""]
    text.append(f"*Telegram ID*\\: `{user.id}`")
    text.append(f"*Имя*\\: {escape_any(get_full_name(user))}")
    text.append(
        f"*Username*\\: {'@' + escape_any(user.username) if user.username else 'Нет'}"
    )
    text.append(f"*Бот\\?*\\: {bool_to_text[user.is_bot]}")
    text.append(f"*Premium\\?*\\: {bool_to_text[user.is_premium]}")
    if groups := await get_user_groups(user.id):
        text.append("*Группы*\\:")
        for group in groups:
            text.append(f"> \\[`{escape_id(group.id)}`\\] {escape_any(group.title)}")
    else:
        text.append("*Группы*\\: Нет")
    return "\n".join(text)

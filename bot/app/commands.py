"""App commands"""

import logging

from contextlib import suppress

# python-telegram-bot
from telegram import (
    KeyboardButton,
    KeyboardButtonRequestChat,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.constants import ChatType
from telegram.ext import ContextTypes

# app helpers
from bot.app.helpers import escape_id, notify

# app kickers
from bot.app.kickers import kick_inside_chat, kick_inside_group

# pyrogram client
from bot.app.pyroclient import update_group_info

# app senders
from bot.app.senders import send_reply

# bot constants
from bot.consts import REQUEST_CHAT

log = logging.getLogger(__name__)


async def command_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows start messages."""
    notify(update, command="/start")
    if args := context.args:
        if args[0] == "group":
            await command_group(update, context)
            return
        with suppress(ValueError):
            if (group_id := int(args[0])) < 0:
                group = await update_group_info(group_id)
                await send_reply(
                    update,
                    f"Группа {group.title} \\[{escape_id(group.id)}\\] "
                    "успешно добавлена\\!",
                )
                return
    await send_reply(update, "Привет\\!")


async def command_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows help messages."""
    notify(update, command="/help")
    if update.effective_chat.type != ChatType.PRIVATE:
        await send_reply(
            update,
            f"Вызови [/group](t.me/{context.bot.username}?start=group), "
            "чтобы добавить бота в группу\\.",
        )


async def command_kick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Kick member from all groups."""
    notify(update, command="/kick")
    if not context.bot_data["kick"]:
        context.bot_data["kick"] = {}
    if update.effective_chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        where, kicker = "в группе", kick_inside_group
    else:
        where, kicker = "в чате", kick_inside_chat
    await send_reply(
        update,
        f"Вызвана команда /kick {where} \\[{escape_id(update.effective_chat.id)}\\]\\.",
    )
    await kicker(update, context)


async def command_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompts to choose group to add bot to."""
    notify(update, command="/group")
    if update.effective_chat.type != ChatType.PRIVATE:
        await send_reply(update, "Пожалуйста, используй эту команду в *личном* чате\\.")
        return
    await send_reply(
        update,
        "Выбери группу\\.",
        reply_markup=ReplyKeyboardMarkup(
            (
                (
                    KeyboardButton(
                        "Нажми, чтобы выбрать.",
                        request_chat=KeyboardButtonRequestChat(
                            update.effective_user.id, **REQUEST_CHAT
                        ),
                    ),
                ),
            ),
            resize_keyboard=True,
        ),
    )

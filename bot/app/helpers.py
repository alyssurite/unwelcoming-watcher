"""App helpers"""

import logging

from typing import Any

# python-telegram-bot
from telegram import Update
from telegram.error import Forbidden
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

# pyrogram client
from bot.app.pyroclient import recheck_rights, update_group_info

# app senders
from bot.app.senders import send_error

# bot constants
from bot.consts import GroupStatus

# database getters
from bot.db.getters import check_group

log = logging.getLogger(__name__)


def escape_any(text: Any):
    return escape_markdown(str(text), 2)


def escape_id(some_id: int | str):
    return escape_any(some_id)


def notify(update: Update, *, command: str = None, function: str = None):
    chat = update.effective_chat
    if command:
        log.info(
            "[%d] {%d} %r called command: %r.",
            update.update_id,
            chat.id,
            chat.effective_name,
            command,
        )
    if function:
        log.info(
            "[%d] {%d} %r called function: %r.",
            update.update_id,
            chat.id,
            chat.effective_name,
            function,
        )


async def leave_chat(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    notify(update, function="leave_chat")
    try:
        if await context.bot.leave_chat(chat_id):
            log.info("Leave Chat: Bot left chat [%d].", chat_id)
        else:
            log.info("Leave Chat: Something went wrong while leaving chat [%d].", chat_id)
    except Forbidden:
        log.info("Leave Chat: Bot was kicked from chat [%d].", chat_id)


async def add_or_leave_group(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    shared: bool = False,
):
    notify(update, function="add_or_leave_group")
    chat_id = (
        update.effective_message.chat_shared.chat_id
        if shared
        else update.effective_chat.id
    )
    is_admin, admin_rights = await recheck_rights(chat_id)
    # notify and leave if bot is not an admin
    if not is_admin:
        await send_error(
            update,
            "Бот не является администратором канала или ограничен в правах\\. "
            "Попробуй удалить его из группы и добавить снова\\. "
            f"Или [*нажми сюда*](t.me/{context.bot.username}?"
            f"startgroup={chat_id}&admin=post_messages+edit_messages+"
            "delete_messages+restrict_members+manage_chat)\\.",
        )
        await leave_chat(update, context, chat_id)
        return GroupStatus.NOT_ADMIN, is_admin, admin_rights
    # notify and leave if bot doesn't have appropriate rights
    if not admin_rights["can_restrict_members"]:
        await send_error(
            update,
            "У бота нет прав на ограничение и удаление участников\\. "
            "Попробуй удалить его из группы и добавить снова\\. "
            f"Или [*нажми сюда*](t.me/{context.bot.username}?"
            f"startgroup={chat_id}&admin=post_messages+edit_messages+"
            "delete_messages+restrict_members+manage_chat)\\.",
        )
        await leave_chat(update, context, chat_id)
        return GroupStatus.RIGHTLESS_ADMIN, is_admin, admin_rights
    # check if group is known
    if await check_group(chat_id):
        return GroupStatus.ALREADY_PRESENT, is_admin, admin_rights
    if not shared:
        await update_group_info(chat_id, is_admin, admin_rights)
    return GroupStatus.RIGHTFUL_ADMIN, is_admin, admin_rights

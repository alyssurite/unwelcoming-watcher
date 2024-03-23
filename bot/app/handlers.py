"""Handlers module"""

import logging

# python-telegram-bot
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from bot.consts import GroupStatus
from bot.app.helpers import add_or_leave_group, notify
from bot.app.pyroclient import update_group_info, update_user_info
from bot.app.senders import send_reply

log = logging.getLogger(__name__)


async def handle_new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    notify(update, function="handle_new_chat_members")
    users = update.message.new_chat_members
    status, *_ = await add_or_leave_group(update, context)
    if status >= GroupStatus.RIGHTFUL_ADMIN:
        for user in users:
            await update_user_info(update.effective_chat.id, user.id)


async def handle_left_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    notify(update, function="handle_left_chat_member")
    user = update.message.left_chat_member
    status, *_ = await add_or_leave_group(update, context)
    if status >= GroupStatus.RIGHTFUL_ADMIN:
        await update_user_info(update.effective_chat.id, user.id)


async def handle_chat_shared(update: Update, context: ContextTypes.DEFAULT_TYPE):
    notify(update, function="handle_chat_shared")
    chat_id = update.effective_message.chat_shared.chat_id
    status, is_admin, admin_rights = await add_or_leave_group(
        update, context, shared=True
    )
    if status < GroupStatus.RIGHTFUL_ADMIN:
        return
    # everything is successful
    await send_reply(
        update,
        "Бот администратор этого чата и имеет права на удаление\\.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await send_reply(
        update,
        "Обновляю информацию о чате\\.\\.\\.",
    )
    await update_group_info(chat_id, is_admin, admin_rights)
    await send_reply(
        update,
        "Информация о чате успешно обновлена\\.\\.\\.",
    )

"""App kickers"""

import logging

from contextlib import suppress

# python-telegram-bot
from telegram import Message, Update
from telegram.constants import MessageEntityType
from telegram.error import BadRequest
from telegram.ext import ContextTypes, ConversationHandler

# app formatters
from bot.app.formatters import escape_any, escape_id

# app helpers
from bot.app.helpers import add_user_to_kick_dict

# pyrogram client
from bot.app.pyroclient import get_chat_by_username

# app senders
from bot.app.senders import send_confirmation, send_error, send_reply

# bot constants
from bot.consts import ConversationState

# database getters
from bot.db.getters import get_user, get_user_groups

# database helpers
from bot.db.helpers import fire_user

log = logging.getLogger(__name__)


async def kick_users(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    target_chat: int,
) -> tuple[set[int], set[int]]:
    success, failure = set(), set()
    target = context.bot_data["kick"][target_chat]
    for target_user, target_info in target.items():
        if not target_info["kick"]:
            log.info("Kick User: User [%d] is not marked for kicking.", target_user)
            continue
        if not (user := await get_user(target_user)):
            log.info("Kick User: User [%d] does not exist.", target_user)
        for group in await get_user_groups(user.id):
            try:
                await context.bot.ban_chat_member(group.id, user.id)
                log.info(
                    "Kick Users: Successfully kicked user [%d] from [%d].",
                    user.id,
                    group.id,
                )
                success.add(user.id)
            except BadRequest as e:
                log.error("Kick Users: Error: %s.", e.message)
                failure.add(f"{group.id}:{user.id}")
                log.info(
                    "Kick Users: Failed to kick user [%d] from [%d].",
                    user.id,
                    group.id,
                )
                await context.bot.send_message(
                    update.effective_user.id,
                    "Не удалось удалить пользователя из чата "
                    f"{escape_any(group.title)!r} "
                    f"\\[{escape_id(group.id)}\\]\\.",
                )
        else:
            if await fire_user(user.id):
                log.info("Kick Users: Fired user [%d].", user.id)
    # delete chat key
    context.bot_data["kick"].pop(target_chat)
    return success, failure


async def process_entities(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    message: Message,
):
    for entity in message.entities:
        # there's @username
        if entity.type == MessageEntityType.MENTION:
            username = message.text[entity.offset : entity.offset + entity.length]
            if chat := await get_chat_by_username(username):
                await add_user_to_kick_dict(context, chat_id, chat.id)
        # no @username
        elif entity.type == MessageEntityType.TEXT_MENTION:
            await add_user_to_kick_dict(context, chat_id, entity.user.id)


async def process_args(
    context: ContextTypes.DEFAULT_TYPE,
    group_id: int,
):
    if not context.args:
        return
    for arg in context.args:
        with suppress(ValueError):
            user_id = int(arg)
            if user_id > 0:
                await add_user_to_kick_dict(context, group_id, user_id)


async def kick_inside_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    group = update.effective_chat
    if (origin := message.reply_to_message) and (user := origin.from_user):
        await add_user_to_kick_dict(context, group.id, user.id)
    else:
        await process_entities(context, group.id, message)
        await process_args(context, group.id)
    if context.bot_data["kick"].get(group.id):
        context.chat_data["query"] = await send_confirmation(update, context, group.id)
        return ConversationState.KICK_QUERY
    await send_error(update, "Не найден ни один пользователь к исключению\\.")
    return ConversationHandler.END


async def kick_inside_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    await process_entities(context, chat.id, message)
    await process_args(context, chat.id)
    if context.bot_data["kick"].get(chat.id):
        context.chat_data["query"] = await send_confirmation(update, context, chat.id)
        return ConversationState.KICK_QUERY
    context.chat_data["query"] = await send_reply(
        update,
        "Перешли сообщение пользователя для исключения\\.\n"
        "Отправь команду */cancel*, чтобы отменить это действие\\.",
    )
    return ConversationState.KICK_WAITING

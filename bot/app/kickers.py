"""App kickers"""


import logging

# python-telegram-bot
from telegram import Chat, Message, Update
from telegram.constants import MessageEntityType
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from bot.app.pyroclient import get_chat_by_username

# app senders
from bot.app.senders import send_confirmation, send_error

# database getters
from bot.db.getters import get_user, get_user_groups

# database helpers
from bot.db.helpers import fire_user

# pyrogram client
from .helpers import escape_any, escape_id

log = logging.getLogger(__name__)


async def add_user_to_kick_dict(
    group_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE
):
    if not (group := context.bot_data["kick"].get(group_id)):
        group = context.bot_data["kick"][group_id] = {}
    group[user_id] = {"kick": False}


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
                context.bot.send_message(
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
    message: Message,
    group: Chat,
):
    for entity in message.entities:
        # there's @username
        if entity.type == MessageEntityType.MENTION:
            username = message.text[entity.offset : entity.offset + entity.length]
            if chat := await get_chat_by_username(username):
                await add_user_to_kick_dict(group.id, chat.id, context)
        # no @username
        elif entity.type == MessageEntityType.TEXT_MENTION:
            await add_user_to_kick_dict(group.id, entity.user.id, context)


async def kick_inside_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    group = update.effective_chat
    if (origin := message.reply_to_message) and (user := origin.from_user):
        await add_user_to_kick_dict(group.id, user.id, context)
    else:
        await process_entities(context, message, group)
    if context.bot_data["kick"]:
        await send_confirmation(update, group)
        return
    await send_error(update, "Не найден ни один пользователь к исключению\\.")


async def kick_inside_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.info("Not available.")

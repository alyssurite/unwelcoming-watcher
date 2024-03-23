"""App kickers"""


import logging

# python-telegram-bot
from telegram import Chat, Message, Update
from telegram.constants import MessageEntityType
from telegram.error import BadRequest
from telegram.ext import ContextTypes

# pyrogram client
from bot.app.pyroclient import get_chat_by_username

# app senders
from bot.app.senders import send_confirmation, send_error

# database getters
from bot.db.getters import get_user, get_user_groups

# database helpers
from bot.db.helpers import fire_user

log = logging.getLogger(__name__)


def add_user_to_kick_dict(
    group_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE
):
    if not (group := context.chat_data["kick"].get(group_id)):
        group = context.chat_data["kick"][group_id] = []
    group.append({"id": user_id, "kick": False})


async def kick_users(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    target_chat: int,
) -> tuple[set[int], set[int]]:
    success, failure = set(), set()
    for kick_user in context.chat_data["kick"][target_chat]:
        if not kick_user["kick"]:
            log.info("Kick User: User [%d] is not marked for kicking.", kick_user["id"])
            continue
        if not (user := await get_user(kick_user["id"])):
            log.info("Kick User: User [%d] does not exist.", kick_user["id"])
        for group in await get_user_groups(user.id):
            try:
                await context.bot.ban_chat_member(group.id, user["id"])
                log.info(
                    "Kick Users: Successfully kicked [%d] from [%d].",
                    user["id"],
                    group.id,
                )
                # probably no need to update database for user here?
                # since bot generates left_chat_member messages
                success.add(user["id"])
            except BadRequest as e:
                failure.add(f"{group.id}:{user['id']}")
                log.info(
                    "Kick Users: Couldn't kick [%d] from [%d].", user["id"], group.id
                )
                log.error("Error: %s.", e.message)
        else:
            if await fire_user(user["id"]):
                log.info("Kick Users: Fired user [%d].", user["id"])
    return success, failure


async def process_entities(
    message: Message, group: Chat, context: ContextTypes.DEFAULT_TYPE
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
    await process_entities(message, group, context)
    if context.chat_data["kick"]:
        await send_confirmation(update, group)
        return
    if (origin := message.reply_to_message) and (user := origin.from_user):
        group.append({"id": user.id, "kick": False})
        await send_confirmation(update, group)
        return
    await send_error(update, "Не найден ни один пользователь к исключению\\.")


async def kick_inside_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.info("Not available.")

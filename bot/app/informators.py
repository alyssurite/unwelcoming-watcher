"""App kickers"""

import logging

from contextlib import suppress

# python-telegram-bot
from telegram import Message, Update
from telegram.constants import MessageEntityType
from telegram.ext import ContextTypes, ConversationHandler

# pyrogram client
from bot.app.pyroclient import get_chat_by_username

# app senders
from bot.app.senders import send_error, send_info, send_reply

# bot constants
from bot.consts import ConversationState

log = logging.getLogger(__name__)


async def process_entities(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    message: Message,
) -> list[Message]:
    info_messages = []
    for entity in message.entities:
        # there's @username
        if entity.type == MessageEntityType.MENTION:
            username = message.text[entity.offset : entity.offset + entity.length]
            if chat := await get_chat_by_username(username):
                if info_message := await send_info(context, chat_id, chat.id):
                    info_messages.append(info_message)
        # no @username
        elif entity.type == MessageEntityType.TEXT_MENTION:
            if info_message := await send_info(context, chat_id, entity.user.id):
                info_messages.append(info_message)
    return info_messages


async def process_args(
    context: ContextTypes.DEFAULT_TYPE,
    group_id: int,
) -> list[Message]:
    info_messages = []
    if not context.args:
        return info_messages
    for arg in context.args:
        with suppress(ValueError):
            user_id = int(arg)
            if user_id > 0:
                if info_message := await send_info(context, group_id, user_id):
                    info_messages.append(info_message)
    return info_messages


async def info_inside_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    group = update.effective_chat
    if (
        (origin := message.reply_to_message)
        and (user := origin.from_user)
        and (await send_info(context, group.id, user.id))
    ):
        return ConversationHandler.END
    else:
        from_entities = await process_entities(context, group.id, message)
        from_args = await process_args(context, group.id)
        if from_entities or from_args:
            return ConversationHandler.END
    await send_error(update, "Укажите пользователя для получения информации\\!")
    return ConversationHandler.END


async def info_inside_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    from_entities = await process_entities(context, chat.id, message)
    from_args = await process_args(context, chat.id)
    if from_entities or from_args:
        return ConversationHandler.END
    context.chat_data["query"] = await send_reply(
        update,
        "Перешли сообщение пользователя для получения информации\\.\n"
        "Отправь команду */cancel*, чтобы отменить это действие\\.",
    )
    return ConversationState.INFO_WAITING

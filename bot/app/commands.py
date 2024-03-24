"""App commands"""

import logging

from contextlib import suppress

# python-telegram-bot
from telegram import (
    KeyboardButton,
    KeyboardButtonRequestChat,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.constants import ChatType
from telegram.ext import ContextTypes, ConversationHandler

# app formatters
from bot.app.formatters import escape_any, escape_id

# app helpers
from bot.app.helpers import notify

# app informators
from bot.app.informators import info_inside_chat, info_inside_group

# app kickers
from bot.app.kickers import kick_inside_chat, kick_inside_group

# pyrogram client
from bot.app.pyroclient import update_group_info, update_user_info

# app senders
from bot.app.senders import send_error, send_reply

# bot constants
from bot.consts import REQUEST_CHAT, ConversationState

# database getters
from bot.db.getters import check_if_superuser, get_user

# database helpers
from bot.db.helpers import grant_user_superuser

# bot settings
from bot.settings import bot_settings

log = logging.getLogger(__name__)


async def command_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows start messages."""
    notify(update, command="/start")
    await update_user_info(update.effective_user.id)
    if args := context.args:
        if args[0] == "group":
            return await command_group(update, context)
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
    await update_user_info(update.effective_user.id)
    if update.effective_chat.type != ChatType.PRIVATE:
        await send_reply(
            update,
            f"Вызови [*/group*](t.me/{context.bot.username}?start=group), "
            "чтобы добавить бота в группу\\.",
        )
        return
    await send_reply(
        update,
        "Вызови */group*, чтобы добавить бота в группу\\.",
    )


async def command_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows help messages."""
    notify(update, command="/info")
    await update_user_info(update.effective_user.id)
    if not await check_if_superuser(update.effective_user.id):
        await send_error(update, "Нет прав на эту команду\\.")
        return
    if update.effective_chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        return await info_inside_group(update, context)
    return await info_inside_chat(update, context)


async def command_kick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Kick member from all groups."""
    notify(update, command="/kick")
    await update_user_info(update.effective_user.id)
    if not await check_if_superuser(update.effective_user.id):
        await send_error(update, "Нет прав на эту команду\\.")
        return
    context.bot_data.setdefault("kick", {})
    if update.effective_chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        return await kick_inside_group(update, context)
    return await kick_inside_chat(update, context)


async def command_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompts to choose group to add bot to."""
    notify(update, command="/group")
    await update_user_info(update.effective_user.id)
    if update.effective_chat.type != ChatType.PRIVATE:
        await send_reply(update, "Пожалуйста, используй эту команду в *личном* чате\\.")
        return ConversationHandler.END
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
    return ConversationState.GROUP_WAITING


async def command_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Grants superuser powers."""
    notify(update, command="/sudo")
    await update_user_info(update.effective_user.id)
    if not (args := context.args):
        log.info("SU: No arguments.")
        return
    if args[0] != bot_settings.su_token:
        log.info("SU: Wrong token.")
        return
    if len(args) > 1:
        user = await get_user(args[1])
    else:
        user = await get_user(update.effective_user.id)
    if not user:
        await send_error(update, "Этот пользователь неизвестен боту\\.")
        return
    if user := await grant_user_superuser(user.id):
        await send_reply(
            update,
            f"Пользователь *{escape_any(user.telegram_full_name)}* \\[`{user.id}`\\] "
            "теперь администратор бота\\.",
        )


async def command_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancel some action."""
    await send_reply(update, "Действие отменено\\.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

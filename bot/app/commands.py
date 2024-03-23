# python-telegram-bot
import logging

from contextlib import suppress

from telegram import (
    KeyboardButton,
    KeyboardButtonRequestChat,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.constants import ChatType
from telegram.ext import ContextTypes

from bot.consts import REQUEST_CHAT
from bot.app.helpers import notify
from bot.app.pyroclient import update_group_info
from bot.app.senders import send_reply

log = logging.getLogger(__name__)


async def command_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows start messages."""
    notify(update, command="/start")
    if context.args:
        with suppress(ValueError):
            if (group_id := int(context.args[0])) < 0:
                await update_group_info(group_id)
    await send_reply(update, "Привет\\!")


async def command_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows help messages."""
    notify(update, command="/help")
    await send_reply(update, "Вызови /group, чтобы добавить бота в группу\\.")


async def command_kick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Kick member from all groups."""
    notify(update, command="/kick")
    await send_reply(update, "Вызови /group, чтобы добавить бота в группу\\.")


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

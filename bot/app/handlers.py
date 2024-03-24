"""App handlers"""

import logging

# python-telegram-bot
from telegram import ReplyKeyboardRemove, Update
from telegram.constants import MessageOriginType
from telegram.ext import ContextTypes, ConversationHandler

# app editors
from bot.app.editors import edit_message

# app formatters
from bot.app.formatters import escape_any, generate_report

# app helpers
from bot.app.helpers import add_or_leave_group, add_user_to_kick_dict, notify

# app kickers
from bot.app.kickers import kick_users

# pyrogram client
from bot.app.pyroclient import update_group_info, update_user_info

# app senders
from bot.app.senders import send_confirmation, send_reply, send_to_superusers

# bot constants
from bot.consts import GroupStatus

# database getters
from bot.db.getters import check_if_fired, check_if_superuser, get_group

# database helpers
from bot.db.helpers import insert_or_update_user

log = logging.getLogger(__name__)


async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # notify(update, function="handle_group_message")
    group_id = update.effective_chat.id
    if await get_group(group_id):
        return
    status, *admin_rights = await add_or_leave_group(update, context)
    if status < GroupStatus.RIGHTFUL_ADMIN:
        return
    await update_group_info(group_id, *admin_rights)


async def handle_status_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    notify(update, function="handle_status_update")
    group_id = update.effective_chat.id
    _, *admin_rights = await add_or_leave_group(update, context)
    await update_group_info(group_id, *admin_rights)


async def handle_new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    notify(update, function="handle_new_chat_members")
    users = update.message.new_chat_members
    status, *_ = await add_or_leave_group(update, context)
    if status < GroupStatus.RIGHTFUL_ADMIN:
        return
    for user in users:
        is_fired, date_fired = await check_if_fired(user.id)
        if is_fired:
            user = await insert_or_update_user(user.id, is_fired=False, date_fired=None)
            await send_to_superusers(
                context,
                f"Пользователь {escape_any(user.telegram_full_name)} "
                f"\\[`{user.id}`\\] был удалён отовсюду "
                f"{date_fired.day:02}\\."
                f"{date_fired.month:02}\\."
                f"{date_fired.year}\\.\n\n"
                "Но теперь он [*добавлен снова*]"
                f"({update.effective_message.link})\\.",
            )
        await update_user_info(update.effective_chat.id, user.id)


async def handle_left_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    notify(update, function="handle_left_chat_member")
    user = update.message.left_chat_member
    status, *_ = await add_or_leave_group(update, context)
    if status < GroupStatus.RIGHTFUL_ADMIN:
        return
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
        "Информация о чате успешно обновлена\\.",
    )


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    notify(update, function="handle_callback_query")
    query = update.callback_query
    await query.answer(query.data, show_alert=True)
    log.info(
        "Callback Query: %r [%d] : [%d] | QUERY from %r [%d]: %r.",
        update.effective_chat.effective_name,
        update.effective_chat.id,
        update.effective_message.message_id,
        update.effective_user.full_name,
        update.effective_user.id,
        query.data,
    )
    if not await check_if_superuser(update.effective_user.id):
        log.info(
            "Callback Query: A user [%d] is not a superuser.",
            update.effective_user.id,
        )
        return
    answer, chat = query.data.split(":")
    target_chat = int(chat)
    if answer != "y":
        log.info("Callback Query: Answer is not positive.")
        log.info("Callback Query: Deleting key...")
        del context.bot_data["kick"][target_chat]
        log.info("Callback Query: Deleted key.")
        await edit_message(update, "Действие отменено\\.")
        return
    target = context.bot_data["kick"][target_chat]
    for user in target:
        target[user]["kick"] = True
    success, failure = await kick_users(update, context, target_chat)
    if not (success or failure):
        log.info("Callback Query: No one was kicked.")
        await edit_message(update, "Никто не был исключён\\.")
        return
    await edit_message(update, await generate_report(success, failure))


async def handle_forwarded_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    notify(update, function="handle_forwarded_message")
    chat = update.effective_chat
    forwarded = update.effective_message.forward_origin
    if forwarded.type not in (MessageOriginType.USER, MessageOriginType.HIDDEN_USER):
        await send_reply(update, "Сообщение не от пользователя\\!")
        return "W"
    if forwarded.type == MessageOriginType.HIDDEN_USER:
        await send_reply(
            update,
            "К сожалению, данный пользователь скрывает свой профиль\\. "
            "Попробуйте удалить его другим способом\\.",
        )
        return "W"
    await add_user_to_kick_dict(context, chat.id, forwarded.sender_user.id)
    if context.bot_data["kick"].get(chat.id):
        await send_confirmation(update, context, chat.id)
    return ConversationHandler.END


async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    notify(update, function="handle_other_messages")
    await send_reply(update, "*Перешли* сообщение, не надо отправлять своё\\.")
    return "W"

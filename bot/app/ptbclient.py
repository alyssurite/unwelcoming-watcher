"""Python-Telegram-Bot client"""

import logging

# python-telegram-bot
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Defaults,
    MessageHandler,
    PicklePersistence,
    filters,
)

# bot commands
from bot.app.commands import (
    command_cancel,
    command_group,
    command_help,
    command_kick,
    command_start,
    command_sudo,
)

# bot handlers
from bot.app.handlers import (
    handle_callback_query,
    handle_chat_shared,
    handle_forwarded_message,
    handle_group_message,
    handle_left_chat_member,
    handle_new_chat_members,
    handle_other_messages,
    handle_status_update,
)

# bot events
from bot.app.on_events import on_bot_init, on_bot_stop

# bot settings
from bot.settings import bot_settings

log = logging.getLogger(__name__)


def build_application() -> Application:
    application = (
        ApplicationBuilder()
        .token(bot_settings.bot_token)
        .persistence(
            persistence=PicklePersistence(
                filepath=bot_settings.persist_file,
            )
        )
        .defaults(
            Defaults(
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_notification=True,
                disable_web_page_preview=True,
                quote=True,
            )
        )
        .post_init(on_bot_init)
        .post_stop(on_bot_stop)
        .build()
    )

    # add to group as admin
    application.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler(
                    "group",
                    command_group,
                ),
                CommandHandler(
                    "start",
                    command_start,
                    has_args=True,
                ),
            ],
            states={
                "X": [
                    MessageHandler(
                        filters.StatusUpdate.CHAT_SHARED,
                        handle_chat_shared,
                    ),
                ],
            },
            fallbacks=[
                CommandHandler(
                    "cancel",
                    command_cancel,
                ),
            ],
            per_chat=True,
            persistent=True,
            name="group_handler",
        ),
    )

    # kick from all groups
    application.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler(
                    "kick",
                    command_kick,
                ),
            ],
            states={
                "W": [
                    MessageHandler(
                        filters.FORWARDED,
                        handle_forwarded_message,
                    ),
                    MessageHandler(
                        ~filters.FORWARDED & ~filters.COMMAND,
                        handle_other_messages,
                    ),
                ]
            },
            fallbacks=[
                CommandHandler(
                    "cancel",
                    command_cancel,
                ),
            ],
            per_chat=True,
            persistent=True,
            name="kick_handler",
        ),
    )

    # start the bot command
    application.add_handler(
        CommandHandler(
            "start",
            command_start,
        ),
    )

    # ask for help command
    application.add_handler(
        CommandHandler(
            "help",
            command_help,
        ),
    )

    # make me a superuser
    application.add_handler(
        CommandHandler(
            "sudo",
            command_sudo,
        ),
    )

    # catch new members
    application.add_handler(
        MessageHandler(
            filters.ChatType.GROUPS & filters.StatusUpdate.NEW_CHAT_MEMBERS,
            handle_new_chat_members,
        ),
    )

    # catch left members
    application.add_handler(
        MessageHandler(
            filters.ChatType.GROUPS & filters.StatusUpdate.LEFT_CHAT_MEMBER,
            handle_left_chat_member,
        ),
    )

    # handle callback queries
    application.add_handler(
        CallbackQueryHandler(
            handle_callback_query,
        ),
    )

    # catch any status update
    application.add_handler(
        MessageHandler(
            filters.ChatType.GROUPS & filters.StatusUpdate.ALL,
            handle_status_update,
        ),
    )

    # catch anything from groups
    application.add_handler(
        MessageHandler(
            filters.ChatType.GROUPS,
            handle_group_message,
        ),
    )

    return application


ptb_app = build_application()

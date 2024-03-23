"""Python-Telegram-Bot client"""

import logging

# python-telegram-bot
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    Defaults,
    MessageHandler,
    PicklePersistence,
    filters,
)

# bot commands
from bot.app.commands import command_group, command_help, command_kick, command_start

# bot handlers
from bot.app.handlers import (
    handle_callback_query,
    handle_chat_shared,
    handle_left_chat_member,
    handle_new_chat_members,
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

    # add to group as admin command
    application.add_handler(
        CommandHandler(
            "group",
            command_group,
        ),
    )

    # kick from all groups
    application.add_handler(
        CommandHandler(
            "kick",
            command_kick,
        ),
    )

    # remove keyboard when chat is shared
    application.add_handler(
        MessageHandler(
            filters.StatusUpdate.CHAT_SHARED,
            handle_chat_shared,
        )
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

    return application


ptb_app = build_application()

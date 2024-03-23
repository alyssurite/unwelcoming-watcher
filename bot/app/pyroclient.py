"""Pyrogram client"""

import logging

from datetime import datetime

from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import ChannelInvalid, PeerIdInvalid
from pyrogram.types import ChatMember

from bot.consts import MEMBER_ABSENT, MEMBER_ADMIN, PRIVILEGES
from bot.db.helpers import (
    insert_or_update_group,
    insert_or_update_group_user,
    insert_or_update_user,
)
from bot.db.updaters import update_group_admin_rights
from bot.settings import bot_settings

log = logging.getLogger(__name__)

pyro_app = Client(
    "unwelcoming_watcher_bot",
    api_id=bot_settings.api_id,
    api_hash=bot_settings.api_hash,
    bot_token=bot_settings.bot_token,
)


def extract_rights(member: ChatMember):
    return {privilege: getattr(member.privileges, privilege) for privilege in PRIVILEGES}


async def recheck_rights(chat_id: int) -> tuple[bool, dict]:
    try:
        bot_info = await pyro_app.get_chat_member(chat_id, pyro_app.me.id)
    except ChannelInvalid:
        return (False, {})
    if bot_info.status != ChatMemberStatus.ADMINISTRATOR:
        return (False, {})
    rights = extract_rights(bot_info)
    return (True, rights)


async def update_rights(chat_id: int) -> tuple[bool, dict]:
    admin = await recheck_rights(chat_id)
    await update_group_admin_rights(chat_id, *admin)
    return admin


async def save_media(file_id: str, file_dir: str, file_name: str):
    if (file_path := bot_settings.cache_dir / file_dir / file_name).exists():
        log.info("Save Media: Media is already saved.")
        return
    log.info("Save Media: Saving %s...", file_path)
    await pyro_app.download_media(file_id, file_name=str(file_path))


async def save_photo(file_id: str):
    await save_media(file_id, "photo", f"{file_id}.jpg")


def check_if_member_admin(member: ChatMember):
    return member.status in MEMBER_ADMIN


def check_if_member_absent(member: ChatMember):
    return member.status in MEMBER_ABSENT


def get_absent_date(member: ChatMember):
    if check_if_member_absent(member):
        return datetime.now().date()
    return None


async def update_member_info(group_id: int, member: ChatMember):
    tg_user = member.user
    user = await insert_or_update_user(
        tg_user.id,
        telegram_first_name=tg_user.first_name,
        telegram_last_name=tg_user.last_name,
        username=tg_user.username,
        is_bot=tg_user.is_bot,
    )
    log.info(
        "Update Member Info: [%d] %r @%s.",
        user.id,
        user.telegram_full_name,
        user.username if tg_user.username else "×",
    )
    await insert_or_update_group_user(
        group_id,
        user.id,
        is_admin=check_if_member_admin(member),
        is_absent=check_if_member_absent(member),
        date_absent=get_absent_date(member),
    )
    return user


async def update_user_info(group_id: int, user_id: int):
    try:
        member = await pyro_app.get_chat_member(group_id, user_id)
    except PeerIdInvalid:
        log.info("A user [%d] left or was banned, but we can't get info.", user_id)
        log.info("Just marking him absent then.")
        await insert_or_update_group_user(
            group_id,
            user_id,
            is_admin=False,
            is_absent=True,
            date_absent=datetime.now().date(),
        )
        return
    await update_member_info(group_id, member)


async def update_group_info(
    group_id: int,
    is_admin: bool = False,
    admin_rights: dict = None,
) -> None:
    # add or update group
    tg_group = await pyro_app.get_chat(group_id)
    group = await insert_or_update_group(
        group_id,
        title=tg_group.title,
        is_admin=is_admin,
        admin_rights=admin_rights,
        public_link=tg_group.username,
        invite_link=tg_group.invite_link,
    )
    async for member in pyro_app.get_chat_members(group_id):
        user = await update_member_info(group_id, member)
        log.info(
            "Update Chat Info: [%d] %r @%s < [%d] %r.",
            user.id,
            user.telegram_full_name,
            user.username,
            group.id,
            group.title,
        )
        # for future use?
        # await save_photo(member.user.photo.big_file_id)

"""Database inserters"""

import logging

from datetime import datetime
from typing import Optional

from bot.db import Session
from bot.db.getters import convert_group, convert_user
from bot.db.models import Group, User, UserGroupAssociation
from bot.db.types import GroupID, UserID

log = logging.getLogger(__name__)


async def insert_group(
    group_id: int,
    title: str = None,
    is_admin: bool = False,
    admin_rights: dict = None,
    public_link: str = None,
    invite_link: str = None,
) -> Group:
    if not admin_rights:
        admin_rights = {}
    with Session.begin() as session:
        session.add(
            group := Group(
                id=group_id,
                title=title,
                is_admin=is_admin,
                **admin_rights,
                public_link=public_link,
                invite_link=invite_link,
            )
        )
        return group


async def insert_user(
    user_id: int,
    *,
    telegram_first_name: str = None,
    telegram_last_name: str = None,
    username: str = None,
    is_superuser: bool = False,
    state_info: dict = None,
    is_bot: bool = False,
) -> User:
    with Session.begin() as session:
        session.add(
            user := User(
                id=user_id,
                telegram_first_name=telegram_first_name,
                telegram_last_name=telegram_last_name,
                username=username,
                is_superuser=is_superuser,
                state_info=state_info,
                is_bot=is_bot,
            )
        )
        return user


async def insert_group_user(
    group: GroupID,
    user: UserID,
    *,
    is_admin: bool = False,
    is_absent: bool = False,
    date_absent: datetime = None,
) -> Optional[UserGroupAssociation]:
    with Session.begin() as session:
        group, user = await convert_group(group), await convert_user(user)
        if group and user:
            session.add(
                group_user := UserGroupAssociation(
                    user=user,
                    group=group,
                    is_admin=is_admin,
                    is_absent=is_absent,
                    date_absent=date_absent,
                )
            )
            return group_user

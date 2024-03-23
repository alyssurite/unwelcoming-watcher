"""Database updaters"""

import logging

from typing import Optional

from bot.consts import PRIVILEGES
from bot.db import Session
from bot.db.getters import get_group, get_group_user, get_user
from bot.db.models import Group, User, UserGroupAssociation
from bot.db.types import GroupID, UserID

log = logging.getLogger(__name__)


async def update_group(group_id: int, **kwargs) -> Optional[Group]:
    with Session.begin() as session:
        if group := await get_group(group_id):
            session.add(group)
            for key, value in kwargs.items():
                setattr(group, key, value)
        return group


async def update_user(user_id: int, **kwargs) -> Optional[User]:
    with Session.begin() as session:
        if user := await get_user(user_id):
            session.add(user)
            for key, value in kwargs.items():
                setattr(user, key, value)
        return user


async def update_group_user(
    group: GroupID,
    user: UserID,
    **kwargs,
) -> Optional[UserGroupAssociation]:
    with Session.begin() as session:
        if group_user := await get_group_user(group, user):
            session.add(group_user)
            for key, value in kwargs.items():
                setattr(group_user, key, value)
        return group_user


async def update_group_admin_rights(
    group_id: int,
    is_admin: bool,
    admin_rights: dict,
) -> Optional[Group]:
    with Session.begin() as session:
        if group := await get_group(group_id):
            session.add(group)
            group.is_admin = is_admin
            for privilege in PRIVILEGES:
                setattr(group, privilege, admin_rights.get(privilege, None))
        return group

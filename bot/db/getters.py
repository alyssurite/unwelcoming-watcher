"""Database getters"""

import logging

from typing import Optional

from sqlalchemy import select

from bot.db import Session
from bot.db.models import Group, User, UserGroupAssociation

log = logging.getLogger(__name__)


async def check_group(group_id: int) -> bool:
    return bool(await get_group(group_id))


async def get_group(group_id: int) -> Optional[Group]:
    with Session() as session:
        return session.get(Group, group_id)


async def check_if_admin(group_id: int) -> bool:
    if group := await get_group(group_id):
        return group.is_admin
    return False


async def check_admin_right(
    group_id: int,
    admin_right: str = "can_restrict_members",
) -> bool:
    if (group := await get_group(group_id)) and getattr(group, admin_right, None):
        return True
    return False


async def convert_group(group: int | Group) -> Optional[Group]:
    if isinstance(group, int) and not (group := await get_group(group)):
        log.warning("Group User: No group supplied.")
    return group


async def get_user(user_id: int) -> Optional[User]:
    with Session() as session:
        return session.get(User, user_id)


async def convert_user(user: int | User) -> Optional[User]:
    if isinstance(user, int) and not (user := await get_user(user)):
        log.warning("Group User: No user supplied.")
    return user


async def get_group_user(
    group: int | Group,
    user: int | User,
) -> Optional[UserGroupAssociation]:
    with Session() as session:
        group, user = await convert_group(group), await convert_user(user)
        if group and user:
            return session.scalars(
                select(UserGroupAssociation).where(
                    UserGroupAssociation.user_id == user.id,
                    UserGroupAssociation.group_id == group.id,
                )
            ).one_or_none()

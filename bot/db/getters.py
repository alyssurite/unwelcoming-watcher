"""Database getters"""

import logging

from datetime import date
from typing import Optional

from sqlalchemy import select

from bot.db import Session
from bot.db.models import Group, User, UserGroupAssociation
from bot.db.types import GroupID, UserID

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
        log.warning("Convert Group: No group supplied.")
    return group


async def get_user(user_id: int) -> Optional[User]:
    with Session() as session:
        return session.get(User, user_id)


async def get_superusers() -> list[User]:
    with Session() as session:
        return session.scalars(select(User).where(User.is_superuser.is_(True))).all()


async def convert_user(user: int | User) -> Optional[User]:
    if isinstance(user, int) and not (user := await get_user(user)):
        log.warning("Convert User: No user supplied.")
    return user


async def check_if_superuser(user_id: int) -> bool:
    if user := await get_user(user_id):
        return user.is_superuser
    return False


async def check_if_fired(user_id: int) -> tuple[bool, Optional[date]]:
    if user := await get_user(user_id):
        return user.is_fired, user.date_fired
    return False, None


async def check_if_absent(group: GroupID, user: UserID) -> tuple[bool, Optional[date]]:
    with Session() as session:
        group, user = await convert_group(group), await convert_user(user)
        if group and user:
            return session.scalars(
                select(
                    UserGroupAssociation.is_absent, UserGroupAssociation.date_absent
                ).where(
                    UserGroupAssociation.user_id == user.id,
                    UserGroupAssociation.group_id == group.id,
                )
            ).one_or_none()
    return False, None


async def get_user_groups(user_id: int) -> list[Group]:
    with Session() as session:
        return session.scalars(
            select(Group)
            .join(UserGroupAssociation)
            .join(User)
            .where(UserGroupAssociation.user_id == user_id)
        ).all()


async def get_users(user_ids: list[int]) -> list[User]:
    with Session() as session:
        return session.scalars(select(User).where(User.id.in_(user_ids))).all()


async def get_group_user(group: GroupID, user: UserID) -> Optional[UserGroupAssociation]:
    with Session() as session:
        group, user = await convert_group(group), await convert_user(user)
        if group and user:
            return session.scalars(
                select(UserGroupAssociation).where(
                    UserGroupAssociation.user_id == user.id,
                    UserGroupAssociation.group_id == group.id,
                )
            ).one_or_none()

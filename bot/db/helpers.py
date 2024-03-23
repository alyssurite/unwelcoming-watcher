"""Database helpers"""

import logging

from datetime import datetime
from typing import Optional

from bot.db.getters import get_group, get_group_user, get_user
from bot.db.inserters import insert_group, insert_group_user, insert_user
from bot.db.models import Group, User, UserGroupAssociation
from bot.db.types import GroupID, UserID
from bot.db.updaters import update_group, update_group_user, update_user

log = logging.getLogger(__name__)


async def insert_or_update_group(group_id: int, **kwargs) -> Optional[Group]:
    if await get_group(group_id):
        return await update_group(group_id, **kwargs)
    return await insert_group(group_id, **kwargs)


async def insert_or_update_user(user_id: int, **kwargs) -> Optional[User]:
    if await get_user(user_id):
        return await update_user(user_id, **kwargs)
    return await insert_user(user_id, **kwargs)


async def insert_or_update_group_user(
    group: GroupID, user: UserID, **kwargs
) -> Optional[UserGroupAssociation]:
    if await get_group_user(group, user):
        return await update_group_user(group, user, **kwargs)
    return await insert_group_user(group, user, **kwargs)


async def fire_user(user_id: int) -> Optional[User]:
    return await update_user(
        user_id,
        is_fired=True,
        date_fired=datetime.now().date(),
    )


async def grant_user_superuser(user_id: int) -> Optional[User]:
    return await update_user(user_id, is_superuser=True)

"""Database schema"""

from datetime import date
from typing import Annotated, List, Optional

# sqlalchemy modules
from sqlalchemy import JSON, BigInteger, Date, ForeignKey, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

# get declarative base class
from . import Base

null_or_str = Annotated[Optional[str], mapped_column(nullable=True)]
bool_false = Annotated[bool, mapped_column(default=False)]


class UserGroupAssociation(Base):
    """Telegram user—group relationship"""

    __tablename__ = "user_group"

    # LEFT: group
    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"), primary_key=True)

    group: Mapped["Group"] = relationship(back_populates="users")

    # RIGHT: user
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)

    user: Mapped["User"] = relationship(back_populates="groups")

    # admin?
    is_admin: Mapped[bool_false]

    # banned or left?
    is_absent: Mapped[bool_false]
    date_absent: Mapped[Optional[date]] = mapped_column(Date)


class User(Base):
    """Telegram user data"""

    __tablename__ = "user"

    # telegram id
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)

    # telegram name
    telegram_first_name: Mapped[str] = mapped_column(String)
    telegram_last_name: Mapped[null_or_str] = mapped_column(String)

    @hybrid_property
    def telegram_full_name(self):
        if self.telegram_last_name:
            return self.telegram_first_name + " " + self.telegram_last_name
        return self.telegram_first_name

    # real name
    first_name: Mapped[null_or_str] = mapped_column(String)
    last_name: Mapped[null_or_str] = mapped_column(String)
    middle_name: Mapped[null_or_str] = mapped_column(String)

    @hybrid_property
    def full_name(self):
        if not self.first_name:
            return
        if not self.last_name:
            return self.first_name
        return self.first_name + " " + self.last_name

    # username
    username: Mapped[null_or_str]

    # superuser?
    is_superuser: Mapped[bool_false]

    # state info
    state_info: Mapped[Optional[dict]] = mapped_column(JSON)

    # bot?
    is_bot: Mapped[bool_false]

    # fired?
    is_fired: Mapped[bool_false]
    date_fired: Mapped[Optional[date]] = mapped_column(Date)

    # RELATIONS

    # RL: M-M user groups
    groups: Mapped[List["UserGroupAssociation"]] = relationship(back_populates="user")


class Group(Base):
    """Telegram group data"""

    __tablename__ = "group"

    # telegram id
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)

    # title
    title: Mapped[null_or_str]

    # admin?
    is_admin: Mapped[bool_false]

    # admin privileges
    can_change_info: Mapped[bool_false]
    can_delete_messages: Mapped[bool_false]
    can_edit_messages: Mapped[bool_false]
    can_invite_users: Mapped[bool_false]
    can_manage_chat: Mapped[bool_false]
    can_manage_video_chats: Mapped[bool_false]
    can_pin_messages: Mapped[bool_false]
    can_post_messages: Mapped[bool_false]
    can_promote_members: Mapped[bool_false]
    can_restrict_members: Mapped[bool_false]
    is_anonymous: Mapped[bool_false]

    # group public link
    public_link: Mapped[null_or_str]

    # invite link
    invite_link: Mapped[null_or_str]

    # RELATIONS

    # RL: M-M group users
    users: Mapped[List["UserGroupAssociation"]] = relationship(back_populates="group")

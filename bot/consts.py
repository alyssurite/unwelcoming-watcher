"""Bot constants"""

from enum import Enum, auto

# pyrogram
from pyrogram.enums import ChatMemberStatus

# python-telegram-bot
from telegram import ChatAdministratorRights


class GroupStatus(Enum):
    NOT_ADMIN = auto()
    RIGHTLESS_ADMIN = auto()
    RIGHTFUL_ADMIN = auto()
    ALREADY_PRESENT = auto()

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value

    def __le__(self, other):
        return self.value <= other.value

    def __ge__(self, other):
        return self.value >= other.value


PRIVILEGES = (
    "can_change_info",
    "can_delete_messages",
    "can_edit_messages",
    "can_invite_users",
    "can_manage_chat",
    "can_manage_video_chats",
    "can_pin_messages",
    "can_post_messages",
    "can_promote_members",
    "can_restrict_members",
    "is_anonymous",
)

MEMBER_ADMIN = {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}
MEMBER_ABSENT = {ChatMemberStatus.LEFT, ChatMemberStatus.BANNED}

ADMIN_ADMINISTRATOR_RIGHTS = ChatAdministratorRights(
    is_anonymous=False,
    # general
    can_manage_chat=True,
    can_change_info=True,
    # messages
    can_post_messages=True,
    can_edit_messages=True,
    can_delete_messages=True,
    can_pin_messages=True,
    # ban/restrict/invite
    can_restrict_members=True,
    can_invite_users=True,
    # stories
    can_post_stories=False,
    can_edit_stories=False,
    can_delete_stories=False,
    # other
    can_manage_topics=False,
    can_manage_video_chats=False,
    can_promote_members=False,
)

BOT_ADMINISTRATOR_RIGHTS = ChatAdministratorRights(
    is_anonymous=False,
    # general
    can_manage_chat=True,
    can_change_info=True,
    # messages
    can_post_messages=True,
    can_edit_messages=True,
    can_delete_messages=True,
    can_pin_messages=True,
    # ban/restrict/invite
    can_restrict_members=True,
    can_invite_users=True,
    # stories
    can_post_stories=False,
    can_edit_stories=False,
    can_delete_stories=False,
    # other
    can_manage_topics=False,
    can_manage_video_chats=False,
    can_promote_members=False,
)

REQUEST_CHAT = {
    "chat_is_channel": False,
    "chat_is_forum": False,
    "bot_is_member": True,
    "user_administrator_rights": ADMIN_ADMINISTRATOR_RIGHTS,
    "bot_administrator_rights": BOT_ADMINISTRATOR_RIGHTS,
}

"""Create tables user, group, user_group

Revision ID: 2f2c99ae26b8
Revises:
Create Date: 2024-03-22 21:01:04.951118

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2f2c99ae26b8"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "group",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column("can_change_info", sa.Boolean(), nullable=False),
        sa.Column("can_delete_messages", sa.Boolean(), nullable=False),
        sa.Column("can_edit_messages", sa.Boolean(), nullable=False),
        sa.Column("can_invite_users", sa.Boolean(), nullable=False),
        sa.Column("can_manage_chat", sa.Boolean(), nullable=False),
        sa.Column("can_manage_video_chats", sa.Boolean(), nullable=False),
        sa.Column("can_pin_messages", sa.Boolean(), nullable=False),
        sa.Column("can_post_messages", sa.Boolean(), nullable=False),
        sa.Column("can_promote_members", sa.Boolean(), nullable=False),
        sa.Column("can_restrict_members", sa.Boolean(), nullable=False),
        sa.Column("is_anonymous", sa.Boolean(), nullable=False),
        sa.Column("public_link", sa.String(), nullable=True),
        sa.Column("invite_link", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("telegram_first_name", sa.String(), nullable=False),
        sa.Column("telegram_last_name", sa.String(), nullable=True),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("middle_name", sa.String(), nullable=True),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("state_info", sa.JSON(), nullable=True),
        sa.Column("is_bot", sa.Boolean(), nullable=False),
        sa.Column("is_fired", sa.Boolean(), nullable=False),
        sa.Column("date_fired", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_group",
        sa.Column("group_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column("is_absent", sa.Boolean(), nullable=False),
        sa.Column("date_absent", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["group.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("group_id", "user_id"),
    )


def downgrade() -> None:
    op.drop_table("user_group")
    op.drop_table("user")
    op.drop_table("group")

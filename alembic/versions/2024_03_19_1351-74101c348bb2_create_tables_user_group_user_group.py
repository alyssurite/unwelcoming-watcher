"""Create tables user, group, user_group

Revision ID: 74101c348bb2
Revises:
Create Date: 2024-03-19 13:51:13.000745

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "74101c348bb2"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "group",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("state_info", sa.JSON(), nullable=True),
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

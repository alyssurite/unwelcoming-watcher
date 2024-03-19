"""Add columns user.is_bot, group.is_admin, group.admin_rights

Revision ID: 7e82f66da9e0
Revises: 74101c348bb2
Create Date: 2024-03-19 19:38:46.221285

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7e82f66da9e0"
down_revision: Union[str, None] = "74101c348bb2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("group", sa.Column("is_admin", sa.Boolean(), nullable=False))
    op.add_column("group", sa.Column("admin_rights", sa.JSON(), nullable=True))
    op.add_column("user", sa.Column("is_bot", sa.Boolean(), nullable=False))


def downgrade() -> None:
    op.drop_column("user", "is_bot")
    op.drop_column("group", "admin_rights")
    op.drop_column("group", "is_admin")

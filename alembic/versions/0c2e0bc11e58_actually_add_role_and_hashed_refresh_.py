"""actually add role and hashed_refresh_token to users

Revision ID: 0c2e0bc11e58
Revises: 
Create Date: 2025-11-18 08:24:48.486434

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c2e0bc11e58'
down_revision: str = 'dbd63ff808b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add 'role' column with server default so existing rows are populated safely
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=50),
                  nullable=False, server_default="user"),
    )

    # Add 'hashed_refresh_token' column (nullable)
    op.add_column(
        "users",
        sa.Column("hashed_refresh_token", sa.String(
            length=255), nullable=True),
    )

    # Optional: remove the server_default if you don't want the DB to keep it:
    # op.alter_column("users", "role", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "hashed_refresh_token")
    op.drop_column("users", "role")

"""Add rate limiting and account lockout fields to User model

Revision ID: add_rate_limiting_fields
Revises: 05575951a36c
Create Date: 2026-06-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_rate_limiting_fields'
down_revision: Union[str, Sequence[str], None] = '05575951a36c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add rate limiting fields to users table."""
    op.add_column('users', sa.Column('failed_attempts', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('is_locked', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    """Downgrade schema - remove rate limiting fields from users table."""
    op.drop_column('users', 'is_locked')
    op.drop_column('users', 'failed_attempts')

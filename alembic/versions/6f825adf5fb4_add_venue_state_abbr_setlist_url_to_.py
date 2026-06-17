"""add venue state_abbr setlist_url to concerts

Revision ID: 6f825adf5fb4
Revises: 0002_remove_album_songs_table
Create Date: 2026-06-17 03:51:23.175980
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '6f825adf5fb4'
down_revision: Union[str, None] = '0002_remove_album_songs_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('concerts', sa.Column('venue', sa.String(length=200), nullable=True))
    op.add_column('concerts', sa.Column('state_abbr', sa.String(length=10), nullable=True))
    op.add_column('concerts', sa.Column('setlist_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column('concerts', 'setlist_url')
    op.drop_column('concerts', 'state_abbr')
    op.drop_column('concerts', 'venue')

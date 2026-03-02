"""Add raw_json columns

Revision ID: 002_add_raw_json
Revises: 001_initial
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_raw_json'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add raw_json column to auction_events
    op.add_column('auction_events', sa.Column('raw_json', sa.JSON(), nullable=True))
    
    # Add raw_json column to auction_items
    op.add_column('auction_items', sa.Column('raw_json', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('auction_items', 'raw_json')
    op.drop_column('auction_events', 'raw_json')

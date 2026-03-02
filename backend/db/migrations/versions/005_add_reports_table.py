"""Add reports table

Revision ID: 005_add_reports
Revises: 004_milestone4
Create Date: 2024-01-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005_add_reports'
down_revision = '004_milestone4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'reports',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('report_type', sa.String(), nullable=False),
        sa.Column('parcel_id', sa.String(), nullable=True),
        sa.Column('event_id', sa.String(), nullable=True),
        sa.Column('file_path', sa.String(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['parcel_id'], ['parcels.id'], ),
        sa.ForeignKeyConstraint(['event_id'], ['auction_events.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reports_id'), 'reports', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_reports_id'), table_name='reports')
    op.drop_table('reports')

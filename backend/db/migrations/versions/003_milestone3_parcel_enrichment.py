"""Milestone 3: Parcel enrichment and comparable sales

Revision ID: 003_milestone3
Revises: 002_add_raw_json
Create Date: 2024-01-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_milestone3'
down_revision = '002_add_raw_json'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new fields to parcels table
    op.add_column('parcels', sa.Column('taxes', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('parcels', sa.Column('assessed_value', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('parcels', sa.Column('flood_flag', sa.Boolean(), nullable=True, server_default=sa.text('0')))
    op.add_column('parcels', sa.Column('last_updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True))
    
    # Create comparable_sales table
    op.create_table(
        'comparable_sales',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('parcel_id_norm', sa.String(), nullable=False),
        sa.Column('comp_id', sa.String(), nullable=False),
        sa.Column('sold_date', sa.Date(), nullable=False),
        sa.Column('sold_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('distance', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('similarity_score', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('raw_json', sa.JSON(), nullable=True),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('acreage', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('zoning', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('comp_id')
    )
    op.create_index(op.f('ix_comparable_sales_id'), 'comparable_sales', ['id'], unique=False)
    op.create_index(op.f('ix_comparable_sales_parcel_id_norm'), 'comparable_sales', ['parcel_id_norm'], unique=False)
    op.create_index(op.f('ix_comparable_sales_comp_id'), 'comparable_sales', ['comp_id'], unique=True)
    op.create_index(op.f('ix_comparable_sales_sold_date'), 'comparable_sales', ['sold_date'], unique=False)
    op.create_index('idx_parcel_sold_date', 'comparable_sales', ['parcel_id_norm', 'sold_date'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_parcel_sold_date', table_name='comparable_sales')
    op.drop_index(op.f('ix_comparable_sales_sold_date'), table_name='comparable_sales')
    op.drop_index(op.f('ix_comparable_sales_comp_id'), table_name='comparable_sales')
    op.drop_index(op.f('ix_comparable_sales_parcel_id_norm'), table_name='comparable_sales')
    op.drop_index(op.f('ix_comparable_sales_id'), table_name='comparable_sales')
    op.drop_table('comparable_sales')
    op.drop_column('parcels', 'last_updated_at')
    op.drop_column('parcels', 'flood_flag')
    op.drop_column('parcels', 'assessed_value')
    op.drop_column('parcels', 'taxes')

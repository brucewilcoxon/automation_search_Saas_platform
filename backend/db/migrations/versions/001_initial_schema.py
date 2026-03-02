"""Initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create counties table
    op.create_table(
        'counties',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('state', sa.String(length=2), nullable=False),
        sa.Column('state_full', sa.String(), nullable=True),
        sa.Column('fips_code', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_counties_id'), 'counties', ['id'], unique=False)
    op.create_index(op.f('ix_counties_name'), 'counties', ['name'], unique=False)
    op.create_index(op.f('ix_counties_state'), 'counties', ['state'], unique=False)

    # Create auction_sources table
    op.create_table(
        'auction_sources',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_url_template', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_auction_sources_id'), 'auction_sources', ['id'], unique=False)
    op.create_index(op.f('ix_auction_sources_name'), 'auction_sources', ['name'], unique=True)

    # Create auction_events table
    op.create_table(
        'auction_events',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('state', sa.String(length=2), nullable=False),
        sa.Column('county', sa.String(), nullable=False),
        sa.Column('county_id', sa.String(), nullable=True),
        sa.Column('event_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='upcoming'),
        sa.Column('source_id', sa.String(), nullable=True),
        sa.Column('source_url', sa.String(), nullable=True),
        sa.Column('item_count', sa.Integer(), nullable=True, server_default='0'),
        sa.ForeignKeyConstraint(['county_id'], ['counties.id'], ),
        sa.ForeignKeyConstraint(['source_id'], ['auction_sources.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auction_events_id'), 'auction_events', ['id'], unique=False)
    op.create_index(op.f('ix_auction_events_county'), 'auction_events', ['county'], unique=False)
    op.create_index(op.f('ix_auction_events_event_date'), 'auction_events', ['event_date'], unique=False)
    op.create_index(op.f('ix_auction_events_state'), 'auction_events', ['state'], unique=False)
    op.create_index(op.f('ix_auction_events_status'), 'auction_events', ['status'], unique=False)

    # Create auction_items table
    op.create_table(
        'auction_items',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('event_id', sa.String(), nullable=False),
        sa.Column('parcel_id_raw', sa.String(), nullable=True),
        sa.Column('parcel_id_norm', sa.String(), nullable=True),
        sa.Column('opening_bid', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='available'),
        sa.Column('item_url', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['auction_events.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auction_items_id'), 'auction_items', ['id'], unique=False)
    op.create_index(op.f('ix_auction_items_event_id'), 'auction_items', ['event_id'], unique=False)
    op.create_index(op.f('ix_auction_items_parcel_id_norm'), 'auction_items', ['parcel_id_norm'], unique=False)
    op.create_index(op.f('ix_auction_items_parcel_id_raw'), 'auction_items', ['parcel_id_raw'], unique=False)
    op.create_index(op.f('ix_auction_items_status'), 'auction_items', ['status'], unique=False)

    # Create parcels table
    op.create_table(
        'parcels',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('auction_id', sa.String(), nullable=True),
        sa.Column('auction_item_id', sa.String(), nullable=True),
        sa.Column('apn', sa.String(), nullable=True),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('county', sa.String(), nullable=True),
        sa.Column('county_id', sa.String(), nullable=True),
        sa.Column('state', sa.String(length=2), nullable=True),
        sa.Column('acreage', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('market_value', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('min_bid', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('zoning', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='available'),
        sa.Column('latitude', sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=10, scale=7), nullable=True),
        sa.ForeignKeyConstraint(['auction_item_id'], ['auction_items.id'], ),
        sa.ForeignKeyConstraint(['county_id'], ['counties.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_parcels_id'), 'parcels', ['id'], unique=False)
    op.create_index(op.f('ix_parcels_apn'), 'parcels', ['apn'], unique=False)
    op.create_index(op.f('ix_parcels_auction_id'), 'parcels', ['auction_id'], unique=False)
    op.create_index(op.f('ix_parcels_county'), 'parcels', ['county'], unique=False)
    op.create_index(op.f('ix_parcels_state'), 'parcels', ['state'], unique=False)
    op.create_index(op.f('ix_parcels_status'), 'parcels', ['status'], unique=False)

    # Create ingest_runs table
    op.create_table(
        'ingest_runs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('source_id', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='running'),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('parcels_processed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('parcels_total', sa.Integer(), nullable=True),
        sa.Column('errors', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['source_id'], ['auction_sources.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ingest_runs_id'), 'ingest_runs', ['id'], unique=False)
    op.create_index(op.f('ix_ingest_runs_source'), 'ingest_runs', ['source'], unique=False)
    op.create_index(op.f('ix_ingest_runs_status'), 'ingest_runs', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_ingest_runs_status'), table_name='ingest_runs')
    op.drop_index(op.f('ix_ingest_runs_source'), table_name='ingest_runs')
    op.drop_index(op.f('ix_ingest_runs_id'), table_name='ingest_runs')
    op.drop_table('ingest_runs')
    op.drop_index(op.f('ix_parcels_status'), table_name='parcels')
    op.drop_index(op.f('ix_parcels_state'), table_name='parcels')
    op.drop_index(op.f('ix_parcels_county'), table_name='parcels')
    op.drop_index(op.f('ix_parcels_auction_id'), table_name='parcels')
    op.drop_index(op.f('ix_parcels_apn'), table_name='parcels')
    op.drop_index(op.f('ix_parcels_id'), table_name='parcels')
    op.drop_table('parcels')
    op.drop_index(op.f('ix_auction_items_status'), table_name='auction_items')
    op.drop_index(op.f('ix_auction_items_parcel_id_raw'), table_name='auction_items')
    op.drop_index(op.f('ix_auction_items_parcel_id_norm'), table_name='auction_items')
    op.drop_index(op.f('ix_auction_items_event_id'), table_name='auction_items')
    op.drop_index(op.f('ix_auction_items_id'), table_name='auction_items')
    op.drop_table('auction_items')
    op.drop_index(op.f('ix_auction_events_status'), table_name='auction_events')
    op.drop_index(op.f('ix_auction_events_state'), table_name='auction_events')
    op.drop_index(op.f('ix_auction_events_event_date'), table_name='auction_events')
    op.drop_index(op.f('ix_auction_events_county'), table_name='auction_events')
    op.drop_index(op.f('ix_auction_events_id'), table_name='auction_events')
    op.drop_table('auction_events')
    op.drop_index(op.f('ix_auction_sources_name'), table_name='auction_sources')
    op.drop_index(op.f('ix_auction_sources_id'), table_name='auction_sources')
    op.drop_table('auction_sources')
    op.drop_index(op.f('ix_counties_state'), table_name='counties')
    op.drop_index(op.f('ix_counties_name'), table_name='counties')
    op.drop_index(op.f('ix_counties_id'), table_name='counties')
    op.drop_table('counties')

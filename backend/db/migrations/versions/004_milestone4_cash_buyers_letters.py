"""Milestone 4: Cash buyers and letter tool

Revision ID: 004_milestone4
Revises: 003_milestone3
Create Date: 2024-01-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004_milestone4'
down_revision = '003_milestone3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create cash_buyers table
    op.create_table(
        'cash_buyers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('company', sa.String(), nullable=True),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('county', sa.String(), nullable=True),
        sa.Column('state', sa.String(length=2), nullable=True),
        sa.Column('purchase_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_purchase_date', sa.Date(), nullable=True),
        sa.Column('total_volume', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('raw_json', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cash_buyers_id'), 'cash_buyers', ['id'], unique=False)
    op.create_index(op.f('ix_cash_buyers_name'), 'cash_buyers', ['name'], unique=False)
    op.create_index(op.f('ix_cash_buyers_company'), 'cash_buyers', ['company'], unique=False)
    op.create_index(op.f('ix_cash_buyers_email'), 'cash_buyers', ['email'], unique=False)
    op.create_index(op.f('ix_cash_buyers_county'), 'cash_buyers', ['county'], unique=False)
    op.create_index(op.f('ix_cash_buyers_state'), 'cash_buyers', ['state'], unique=False)
    op.create_index(op.f('ix_cash_buyers_last_purchase_date'), 'cash_buyers', ['last_purchase_date'], unique=False)
    op.create_index('idx_buyer_location', 'cash_buyers', ['county', 'state'], unique=False)
    op.create_index('idx_buyer_activity', 'cash_buyers', ['last_purchase_date', 'purchase_count'], unique=False)
    
    # Create letter_templates table
    op.create_table(
        'letter_templates',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('subject', sa.String(), nullable=True),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('merge_fields', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_letter_templates_id'), 'letter_templates', ['id'], unique=False)
    
    # Create letter_campaigns table
    op.create_table(
        'letter_campaigns',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('template_id', sa.String(), nullable=False),
        sa.Column('parcel_ids', sa.JSON(), nullable=False),
        sa.Column('merge_fields', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='draft'),
        sa.Column('total_letters', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('sent_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], ['letter_templates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_letter_campaigns_id'), 'letter_campaigns', ['id'], unique=False)
    
    # Create letters table
    op.create_table(
        'letters',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('campaign_id', sa.String(), nullable=False),
        sa.Column('parcel_id', sa.String(), nullable=True),
        sa.Column('recipient_name', sa.String(), nullable=True),
        sa.Column('recipient_email', sa.String(), nullable=True),
        sa.Column('recipient_address', sa.String(), nullable=True),
        sa.Column('subject', sa.String(), nullable=True),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('raw_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['letter_campaigns.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_letters_id'), 'letters', ['id'], unique=False)
    op.create_index(op.f('ix_letters_campaign_id'), 'letters', ['campaign_id'], unique=False)
    op.create_index(op.f('ix_letters_parcel_id'), 'letters', ['parcel_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_letters_parcel_id'), table_name='letters')
    op.drop_index(op.f('ix_letters_campaign_id'), table_name='letters')
    op.drop_index(op.f('ix_letters_id'), table_name='letters')
    op.drop_table('letters')
    op.drop_index(op.f('ix_letter_campaigns_id'), table_name='letter_campaigns')
    op.drop_table('letter_campaigns')
    op.drop_index(op.f('ix_letter_templates_id'), table_name='letter_templates')
    op.drop_table('letter_templates')
    op.drop_index('idx_buyer_activity', table_name='cash_buyers')
    op.drop_index('idx_buyer_location', table_name='cash_buyers')
    op.drop_index(op.f('ix_cash_buyers_last_purchase_date'), table_name='cash_buyers')
    op.drop_index(op.f('ix_cash_buyers_state'), table_name='cash_buyers')
    op.drop_index(op.f('ix_cash_buyers_county'), table_name='cash_buyers')
    op.drop_index(op.f('ix_cash_buyers_email'), table_name='cash_buyers')
    op.drop_index(op.f('ix_cash_buyers_company'), table_name='cash_buyers')
    op.drop_index(op.f('ix_cash_buyers_name'), table_name='cash_buyers')
    op.drop_index(op.f('ix_cash_buyers_id'), table_name='cash_buyers')
    op.drop_table('cash_buyers')

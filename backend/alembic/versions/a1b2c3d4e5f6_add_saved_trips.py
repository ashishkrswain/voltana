"""add saved_trips for trip history

Revision ID: a1b2c3d4e5f6
Revises: 6d24c5ebff09
Create Date: 2026-09-03 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '6d24c5ebff09'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'saved_trips',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('origin_name', sa.String(length=200), nullable=False),
        sa.Column('origin_lat', sa.Float(), nullable=False),
        sa.Column('origin_lng', sa.Float(), nullable=False),
        sa.Column('dest_name', sa.String(length=200), nullable=False),
        sa.Column('dest_lat', sa.Float(), nullable=False),
        sa.Column('dest_lng', sa.Float(), nullable=False),
        sa.Column('assumed_avg_speed_kmph', sa.Float(), nullable=False, server_default='60'),
        sa.Column('starting_battery_pct', sa.Float(), nullable=False, server_default='100'),
        sa.Column('safety_buffer_pct', sa.Float(), nullable=False, server_default='20'),
        sa.Column('total_distance_km', sa.Float(), nullable=False),
        sa.Column('total_estimated_duration_min', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_saved_trips_vehicle_id', 'saved_trips', ['vehicle_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_saved_trips_vehicle_id', table_name='saved_trips')
    op.drop_table('saved_trips')

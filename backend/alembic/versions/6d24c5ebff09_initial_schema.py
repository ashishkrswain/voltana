"""initial schema

Revision ID: 6d24c5ebff09
Revises:
Create Date: 2026-08-20 15:58:19.790626

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6d24c5ebff09'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums
    vehicle_category = postgresql.ENUM(
        'two_wheeler', 'three_wheeler', 'four_wheeler',
        name='vehiclecategory', create_type=False
    )
    vehicle_category.create(op.get_bind(), checkfirst=True)

    vehicle_status = postgresql.ENUM(
        'active', 'discontinued',
        name='vehiclestatus', create_type=False
    )
    vehicle_status.create(op.get_bind(), checkfirst=True)

    range_confidence_level = postgresql.ENUM(
        'high', 'medium', 'low',
        name='rangeconfidencelevel', create_type=False
    )
    range_confidence_level.create(op.get_bind(), checkfirst=True)

    efficiency_source = postgresql.ENUM(
        'manufacturer', 'community', 'estimated',
        name='efficiencysource', create_type=False
    )
    efficiency_source.create(op.get_bind(), checkfirst=True)

    connector_type = postgresql.ENUM(
        'Type 2', 'Bharat AC-001', 'CCS2', 'GB/T',
        'Bharat DC-001', 'CHAdeMO', 'Tesla NACS',
        'Type 6', 'Type 7',
        name='connectortype', create_type=False
    )
    connector_type.create(op.get_bind(), checkfirst=True)

    charger_status = postgresql.ENUM(
        'unknown', 'operational', 'out_of_order', 'maintenance',
        name='chargerstatus', create_type=False
    )
    charger_status.create(op.get_bind(), checkfirst=True)

    # Create tables
    op.create_table(
        'charger_networks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('api_endpoint', sa.String(length=255), nullable=True),
        sa.Column('ocpi_endpoint', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Integer(), nullable=False, server_default='1'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug'),
    )
    op.create_index('ix_charger_networks_name', 'charger_networks', ['name'], unique=False)
    op.create_index('ix_charger_networks_slug', 'charger_networks', ['slug'], unique=False)

    op.create_table(
        'vehicles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category', vehicle_category, nullable=False),
        sa.Column('make', sa.String(length=100), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('variant', sa.String(length=100), nullable=False),
        sa.Column('model_year', sa.Integer(), nullable=False),
        sa.Column('battery_capacity_kwh', sa.Float(), nullable=False),
        sa.Column('battery_chemistry', sa.String(length=50), nullable=True),
        sa.Column('arai_range_km', sa.Integer(), nullable=False),
        sa.Column('real_world_range_km', sa.Integer(), nullable=False),
        sa.Column('top_speed_kmph', sa.Integer(), nullable=True),
        sa.Column('efficiency_wh_per_km', sa.Float(), nullable=False),
        sa.Column('ac_charge_port_type', sa.String(length=50), nullable=True),
        sa.Column('dc_charge_port_type', sa.String(length=50), nullable=True),
        sa.Column('max_ac_charge_kw', sa.Float(), nullable=True),
        sa.Column('max_dc_charge_kw', sa.Float(), nullable=True),
        sa.Column('dc_10_80_time_minutes', sa.Integer(), nullable=True),
        sa.Column('price_ex_showroom_inr', sa.Integer(), nullable=True),
        sa.Column('status', vehicle_status, nullable=False, server_default='active'),
        sa.Column('source_last_verified', sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_vehicles_make', 'vehicles', ['make'], unique=False)
    op.create_index('ix_vehicles_model', 'vehicles', ['model'], unique=False)
    op.create_index('ix_vehicles_variant', 'vehicles', ['variant'], unique=False)
    op.create_index('ix_vehicles_category', 'vehicles', ['category'], unique=False)

    op.create_table(
        'efficiency_curve',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('speed_band_kmph', sa.Integer(), nullable=False),
        sa.Column('wh_per_km', sa.Float(), nullable=False),
        sa.Column('source', efficiency_source, nullable=False, server_default='estimated'),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_efficiency_curve_vehicle_id', 'efficiency_curve', ['vehicle_id'], unique=False)

    op.create_table(
        'range_confidence',
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('confidence', range_confidence_level, nullable=False),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('vehicle_id'),
    )

    op.create_table(
        'chargers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('network_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('connector_types', sa.Text(), nullable=False),
        sa.Column('power_kw', sa.Float(), nullable=False),
        sa.Column('status', charger_status, nullable=False, server_default='unknown'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['network_id'], ['charger_networks.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_chargers_latitude', 'chargers', ['latitude'], unique=False)
    op.create_index('ix_chargers_longitude', 'chargers', ['longitude'], unique=False)
    op.create_index('ix_chargers_network_id', 'chargers', ['network_id'], unique=False)


def downgrade() -> None:
    op.drop_table('chargers')
    op.drop_table('range_confidence')
    op.drop_table('efficiency_curve')
    op.drop_table('vehicles')
    op.drop_table('charger_networks')

    # Drop enums
    charger_status = postgresql.ENUM(name='chargerstatus')
    charger_status.drop(op.get_bind(), checkfirst=True)

    connector_type = postgresql.ENUM(name='connectortype')
    connector_type.drop(op.get_bind(), checkfirst=True)

    efficiency_source = postgresql.ENUM(name='efficiencysource')
    efficiency_source.drop(op.get_bind(), checkfirst=True)

    range_confidence_level = postgresql.ENUM(name='rangeconfidencelevel')
    range_confidence_level.drop(op.get_bind(), checkfirst=True)

    vehicle_status = postgresql.ENUM(name='vehiclestatus')
    vehicle_status.drop(op.get_bind(), checkfirst=True)

    vehicle_category = postgresql.ENUM(name='vehiclecategory')
    vehicle_category.drop(op.get_bind(), checkfirst=True)
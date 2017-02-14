"""station missing line

Revision ID: 4b6d4684ad8
Revises: 10606515099
Create Date: 2017-02-09 11:42:49.073588

"""

# revision identifiers, used by Alembic.
revision = '4b6d4684ad8'
down_revision = '10606515099'

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSON


def upgrade():
    op.create_table('transnet_station_missing_data',
                    sa.Column('id', sa.Integer, nullable=False),
                    sa.Column('geom', geoalchemy2.types.Geometry(geometry_type='POLYGON'), nullable=True),
                    sa.Column('raw_geom', sa.String(), nullable=True),
                    sa.Column('country', sa.String(), nullable=True),
                    sa.Column('tags', JSON),
                    sa.Column('lat', sa.Numeric(), nullable=True),
                    sa.Column('lon', sa.Numeric(), nullable=True),
                    sa.Column('length', sa.Numeric(), nullable=True),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.Column('missing_connection', sa.Boolean(), nullable=False, default=False),
                    sa.Column('voltage', postgresql.ARRAY(sa.INTEGER()), nullable=True),
                    sa.Column('estimated_voltage', postgresql.ARRAY(sa.INTEGER()), nullable=True),
                    sa.Column('osm_id', sa.INTEGER(), nullable=True),
                    sa.Column('type', sa.String(), nullable=True),
                    sa.PrimaryKeyConstraint('id'))

    op.create_index(op.f('ix_transnet_station_missing_data_country'), 'transnet_station_missing_data', ['country'])


def downgrade():
    op.drop_index(op.f('ix_transnet_station_missing_data_country'), table_name='transnet_station_missing_data')
    op.drop_table('transnet_station_missing_data')

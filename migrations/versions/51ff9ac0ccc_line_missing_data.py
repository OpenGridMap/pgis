"""line_missing_data

Revision ID: 51ff9ac0ccc
Revises: 59bbd07a80a
Create Date: 2017-02-02 14:04:17.056892

"""

# revision identifiers, used by Alembic.
revision = '51ff9ac0ccc'
down_revision = '59bbd07a80a'

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSON


def upgrade():
    op.create_table('transnet_line_missing_data',
                    sa.Column('id', sa.Integer, nullable=False),
                    sa.Column('geom', geoalchemy2.types.Geometry(geometry_type='LINESTRING'), nullable=True),
                    sa.Column('country', sa.String(), nullable=True),
                    sa.Column('properties', JSON),
                    sa.Column('srs_geom', geoalchemy2.types.Geometry(geometry_type='LINESTRING'), nullable=True),
                    sa.Column('lat', sa.Numeric(), nullable=True),
                    sa.Column('lon', sa.Numeric(), nullable=True),
                    sa.Column('length', sa.Numeric(), nullable=True),
                    sa.Column('cables', sa.INTEGER(), nullable=True),
                    sa.Column('estimated_cables', postgresql.ARRAY(sa.INTEGER()), nullable=True),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.Column('nodes', postgresql.ARRAY(sa.BIGINT()), nullable=True),
                    sa.Column('osm_id', sa.INTEGER(), nullable=True),
                    sa.Column('raw_geom', sa.String(), nullable=True),
                    sa.Column('voltage', postgresql.ARRAY(sa.INTEGER()), nullable=True),
                    sa.Column('estimated_voltage', postgresql.ARRAY(sa.INTEGER()), nullable=True),
                    sa.Column('osm_id', sa.INTEGER(), nullable=True),
                    sa.PrimaryKeyConstraint('id'))

    op.create_index(op.f('ix_transnet_line_missing_data_country'), 'transnet_line_missing_data', ['country'])


def downgrade():
    op.drop_index(op.f('ix_transnet_line_missing_data_country'), table_name='transnet_line_missing_data')
    op.drop_table('transnet_line_missing_data')

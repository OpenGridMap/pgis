"""empty message

Revision ID: 3f088e2050e
Revises: 1f16ab8212e
Create Date: 2016-09-23 12:58:19.766800

"""

# revision identifiers, used by Alembic.
revision = '3f088e2050e'
down_revision = '1f16ab8212e'

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


def upgrade():
    op.add_column('transnet_powerline', sa.Column('cables', sa.INTEGER(), nullable=True))
    op.add_column('transnet_powerline', sa.Column('lat', sa.INTEGER(), nullable=True))
    op.add_column('transnet_powerline', sa.Column('length', sa.INTEGER(), nullable=True))
    op.add_column('transnet_powerline', sa.Column('lon', sa.INTEGER(), nullable=True))
    op.add_column('transnet_powerline', sa.Column('name', sa.String(), nullable=True))
    op.add_column('transnet_powerline', sa.Column('nodes', postgresql.ARRAY(sa.INTEGER()), nullable=True))
    op.add_column('transnet_powerline', sa.Column('osm_id', sa.INTEGER(), nullable=True))
    op.add_column('transnet_powerline', sa.Column('raw_geom', sa.String(), nullable=True))
    op.add_column('transnet_powerline', sa.Column('tags', postgresql.JSON(), nullable=True))
    op.add_column('transnet_powerline', sa.Column('type', sa.String(), nullable=True))
    op.add_column('transnet_powerline', sa.Column('voltage', postgresql.ARRAY(sa.INTEGER()), nullable=True))
    op.drop_column('transnet_powerline', 'properties')

    op.drop_column('transnet_station', 'properties')
    op.add_column('transnet_station', sa.Column('tags', postgresql.JSON(), nullable=True))
    op.add_column('transnet_station', sa.Column('raw_geom', sa.String(), nullable=True))
    op.add_column('transnet_station', sa.Column('lat', sa.INTEGER(), nullable=True))
    op.add_column('transnet_station', sa.Column('length', sa.INTEGER(), nullable=True))
    op.add_column('transnet_station', sa.Column('lon', sa.INTEGER(), nullable=True))
    op.add_column('transnet_station', sa.Column('name', sa.String(), nullable=True))
    op.add_column('transnet_station', sa.Column('osm_id', sa.INTEGER(), nullable=True))
    op.add_column('transnet_station', sa.Column('nodes', postgresql.ARRAY(sa.INTEGER()), nullable=True))
    op.add_column('transnet_station', sa.Column('voltage', postgresql.ARRAY(sa.INTEGER()), nullable=True))
    op.add_column('transnet_station', sa.Column('type', sa.String(), nullable=True))


def downgrade():
    op.add_column('transnet_powerline', sa.Column('properties', postgresql.JSON(), autoincrement=False, nullable=True))
    op.drop_column('transnet_powerline', 'voltage')
    op.drop_column('transnet_powerline', 'type')
    op.drop_column('transnet_powerline', 'tags')
    op.drop_column('transnet_powerline', 'raw_geom')
    op.drop_column('transnet_powerline', 'osm_id')
    op.drop_column('transnet_powerline', 'nodes')
    op.drop_column('transnet_powerline', 'name')
    op.drop_column('transnet_powerline', 'lon')
    op.drop_column('transnet_powerline', 'length')
    op.drop_column('transnet_powerline', 'lat')
    op.drop_column('transnet_powerline', 'cables')

    op.drop_column('transnet_station', 'tags')
    op.drop_column('transnet_station', 'raw_geom')
    op.drop_column('transnet_station', 'lon')
    op.drop_column('transnet_station', 'length')
    op.drop_column('transnet_station', 'lat')
    op.drop_column('transnet_station', 'name')
    op.drop_column('transnet_station', 'osm_id')
    op.drop_column('transnet_station', 'nodes')
    op.drop_column('transnet_station', 'voltage')
    op.drop_column('transnet_powerline', 'type')

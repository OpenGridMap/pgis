"""empty message

Revision ID: 1ed3d68629f
Revises: 46087859d23
Create Date: 2016-09-23 18:36:03.465649

"""

# revision identifiers, used by Alembic.
import geoalchemy2

revision = '1ed3d68629f'
down_revision = '46087859d23'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.drop_column('transnet_station', 'nodes')

    op.add_column('transnet_powerline',
                  sa.Column('srs_geom', geoalchemy2.types.Geometry(geometry_type='LINESTRING'), nullable=True))


def downgrade():
    op.add_column('transnet_station', sa.Column('nodes', postgresql.ARRAY(sa.BIGINT()), nullable=True))

    op.drop_column('transnet_powerline', 'srs_geom')

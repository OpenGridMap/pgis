"""empty message

Revision ID: 1f16ab8212e
Revises: 58ba1b9ec53
Create Date: 2016-09-15 14:23:30.823686

"""

import geoalchemy2
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision = '1f16ab8212e'
down_revision = '58ba1b9ec53'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.create_table('transnet_powerline',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('geom', geoalchemy2.types.Geometry(geometry_type='LINESTRING'), nullable=True),
                    sa.Column('country', sa.String(), nullable=True),
                    sa.Column('properties', JSON),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('transnet_station',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('geom', geoalchemy2.types.Geometry(geometry_type='POLYGON'), nullable=True),
                    sa.Column('country', sa.String(), nullable=True),
                    sa.Column('properties', JSON),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('transnet_powerline')
    op.drop_table('transnet_station')
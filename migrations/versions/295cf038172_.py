"""empty message

Revision ID: 295cf038172
Revises: 24efceceea3
Create Date: 2016-09-23 17:29:57.967014

"""

# revision identifiers, used by Alembic.
revision = '295cf038172'
down_revision = '24efceceea3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.drop_column('transnet_powerline', 'lat')
    op.drop_column('transnet_powerline', 'lon')
    op.drop_column('transnet_powerline', 'length')

    op.drop_column('transnet_station', 'lat')
    op.drop_column('transnet_station', 'lon')
    op.drop_column('transnet_station', 'length')

    op.add_column('transnet_powerline', sa.Column('lat', sa.Numeric(), nullable=True))
    op.add_column('transnet_powerline', sa.Column('lon', sa.Numeric(), nullable=True))
    op.add_column('transnet_powerline', sa.Column('length', sa.Numeric(), nullable=True))

    op.add_column('transnet_station', sa.Column('lat', sa.Numeric(), nullable=True))
    op.add_column('transnet_station', sa.Column('lon', sa.Numeric(), nullable=True))
    op.add_column('transnet_station', sa.Column('length', sa.Numeric(), nullable=True))


def downgrade():
    op.drop_column('transnet_powerline', 'lat')
    op.drop_column('transnet_powerline', 'lon')
    op.drop_column('transnet_powerline', 'length')

    op.drop_column('transnet_station', 'lat')
    op.drop_column('transnet_station', 'lon')
    op.drop_column('transnet_station', 'length')

    op.add_column('transnet_powerline', sa.Column('lat', sa.Integer(), nullable=True))
    op.add_column('transnet_powerline', sa.Column('lon', sa.Integer(), nullable=True))
    op.add_column('transnet_powerline', sa.Column('length', sa.Integer(), nullable=True))

    op.add_column('transnet_station', sa.Column('lat', sa.Integer(), nullable=True))
    op.add_column('transnet_station', sa.Column('lon', sa.Integer(), nullable=True))
    op.add_column('transnet_station', sa.Column('length', sa.Integer(), nullable=True))

"""adding osm_replications

Revision ID: 21466a6ed49
Revises: 314a3d1f9a5
Create Date: 2016-11-17 11:01:05.756420

"""

# revision identifiers, used by Alembic.
revision = '21466a6ed49'
down_revision = '314a3d1f9a5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('transnet_station', sa.Column('osm_replication', sa.Integer(), nullable=True, default=1))
    op.add_column('transnet_powerline', sa.Column('osm_replication', sa.Integer(), nullable=True, default=1))


def downgrade():
    op.remove_column('transnet_station', 'osm_replication')
    op.remove_column('transnet_powerline', 'osm_replication')

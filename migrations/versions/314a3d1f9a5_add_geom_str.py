"""add geom_str

Revision ID: 314a3d1f9a5
Revises: e5558f7f27
Create Date: 2016-10-27 16:52:02.348434

"""

# revision identifiers, used by Alembic.
revision = '314a3d1f9a5'
down_revision = 'e5558f7f27'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('scigrid_powerline', sa.Column('geom_str', sa.String(), nullable=True))
    op.add_column('scigrid_station', sa.Column('geom_str', sa.String(), nullable=True))


def downgrade():
    op.drop_column('scigrid_powerline', 'geom_str')
    op.drop_column('scigrid_station', 'geom_str')

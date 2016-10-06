"""add_nominal_power

Revision ID: 1664b06a80a
Revises: 1ed3d68629f
Create Date: 2016-10-06 14:16:00.571683

"""

# revision identifiers, used by Alembic.
revision = '1664b06a80a'
down_revision = '1ed3d68629f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('transnet_station', sa.Column('nominal_power', sa.String(), nullable=True))


def downgrade():
    op.remove_column('transnet_station', 'nominal_power')

"""many to many relations

Revision ID: 340badbcba6
Revises: 564d4b52ea2
Create Date: 2016-10-26 11:45:55.121205

"""

# revision identifiers, used by Alembic.
revision = '340badbcba6'
down_revision = '564d4b52ea2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('transnet_powerline', 'relation_id')
    op.drop_column('transnet_station', 'relation_id')


def downgrade():
    op.add_column('transnet_station', sa.Column('relation_id', sa.Integer(), nullable=False))
    op.create_index(op.f('ix_transnet_station_relation_id'), 'transnet_station', ['relation_id'])

    op.add_column('transnet_powerline', sa.Column('relation_id', sa.Integer(), nullable=False))
    op.create_index(op.f('ix_transnet_powerline_relation_id'), 'transnet_powerline', ['relation_id'])

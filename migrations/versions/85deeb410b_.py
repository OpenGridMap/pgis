"""empty message

Revision ID: 85deeb410b
Revises: 201b7349c89
Create Date: 2016-09-23 14:55:52.514339

"""

# revision identifiers, used by Alembic.
revision = '85deeb410b'
down_revision = '201b7349c89'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.add_column('transnet_station', sa.Column('relation_id', sa.Integer(), nullable=False))
    op.create_index(op.f('ix_transnet_station_relation_id'), 'transnet_station', ['relation_id'])

    op.add_column('transnet_powerline', sa.Column('relation_id', sa.Integer(), nullable=False))
    op.create_index(op.f('ix_transnet_powerline_relation_id'), 'transnet_powerline', ['relation_id'])


def downgrade():
    op.drop_column('transnet_powerline', 'relation_id')
    op.drop_column('transnet_station', 'relation_id')

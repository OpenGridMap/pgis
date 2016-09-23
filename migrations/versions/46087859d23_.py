"""empty message

Revision ID: 46087859d23
Revises: 295cf038172
Create Date: 2016-09-23 17:45:35.741373

"""

# revision identifiers, used by Alembic.
revision = '46087859d23'
down_revision = '295cf038172'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.drop_column('transnet_powerline', 'nodes')
    op.drop_column('transnet_station', 'nodes')

    op.add_column('transnet_powerline', sa.Column('nodes', postgresql.ARRAY(sa.BIGINT()), nullable=True))
    op.add_column('transnet_station', sa.Column('nodes', postgresql.ARRAY(sa.BIGINT()), nullable=True))


def downgrade():
    op.drop_column('transnet_powerline', 'nodes')
    op.drop_column('transnet_station', 'nodes')

    op.add_column('transnet_powerline', sa.Column('nodes', postgresql.ARRAY(sa.INTEGER()), nullable=True))
    op.add_column('transnet_station', sa.Column('nodes', postgresql.ARRAY(sa.INTEGER()), nullable=True))

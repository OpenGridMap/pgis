"""line_missing_data_tags

Revision ID: 4153975f210
Revises: 51ff9ac0ccc
Create Date: 2017-02-02 14:48:23.126469

"""

# revision identifiers, used by Alembic.
revision = '4153975f210'
down_revision = '51ff9ac0ccc'

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


def upgrade():
    op.add_column('transnet_line_missing_data', sa.Column('tags', postgresql.JSON(), nullable=True))
    op.drop_column('transnet_line_missing_data', 'properties')


def downgrade():
    op.add_column('transnet_line_missing_data',
                  sa.Column('properties', postgresql.JSON(), autoincrement=False, nullable=True))
    op.drop_column('transnet_line_missing_data', 'tags')

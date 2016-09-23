"""empty message

Revision ID: 3a1fbf8d5a0
Revises: 85deeb410b
Create Date: 2016-09-23 16:20:55.192941

"""

# revision identifiers, used by Alembic.
revision = '3a1fbf8d5a0'
down_revision = '85deeb410b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.add_column('transnet_relation', sa.Column('name', sa.VARCHAR(), nullable=True))


def downgrade():
    op.drop_column('transnet_relation', 'name')

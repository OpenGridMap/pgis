"""empty message

Revision ID: 24efceceea3
Revises: 3a1fbf8d5a0
Create Date: 2016-09-23 16:49:24.548847

"""

# revision identifiers, used by Alembic.
revision = '24efceceea3'
down_revision = '3a1fbf8d5a0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.drop_column('transnet_relation', 'voltage')
    op.add_column('transnet_relation', sa.Column('voltage', sa.Integer, nullable=True))


def downgrade():
    op.drop_column('transnet_relation', 'voltage')
    op.add_column('transnet_relation', sa.Column('voltage', postgresql.ARRAY(sa.INTEGER(), nullable=True)))

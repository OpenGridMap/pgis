"""empty message

Revision ID: 24acc647114
Revises: 29c4a532deb
Create Date: 2015-04-03 13:50:21.492501

"""

# revision identifiers, used by Alembic.
revision = '24acc647114'
down_revision = '29c4a532deb'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


def upgrade():
    op.add_column('point', sa.Column('properties', JSON))
    op.add_column('powerline', sa.Column('properties', JSON))


def downgrade():
    op.remove_column('point', 'properties')
    op.remove_column('powerline', 'properties')


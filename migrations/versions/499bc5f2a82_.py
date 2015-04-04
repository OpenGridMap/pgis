"""empty message

Revision ID: 499bc5f2a82
Revises: 24acc647114
Create Date: 2015-04-03 22:32:22.943236

"""

# revision identifiers, used by Alembic.
revision = '499bc5f2a82'
down_revision = '24acc647114'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

def upgrade():
    op.add_column('user', sa.Column('action_permissions', JSON))

def downgrade():
    op.remove_column('user', 'action_permissions')

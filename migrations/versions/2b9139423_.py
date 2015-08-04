"""empty message

Revision ID: 2b9139423
Revises: 13d7ddfddbc
Create Date: 2015-08-04 18:33:12.811540

"""

# revision identifiers, used by Alembic.
revision = '2b9139423'
down_revision = '13d7ddfddbc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('point', 'name')


def downgrade():
    op.add_column('point', sa.Column('name', sa.String(length=64), nullable=True)) 

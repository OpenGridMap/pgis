"""empty message

Revision ID: 306abdb215f
Revises: 4b6d4684ad8
Create Date: 2017-03-09 03:43:51.215336

"""

# revision identifiers, used by Alembic.
revision = '306abdb215f'
down_revision = '4b6d4684ad8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('point', sa.Column('deleted_by_user', sa.Boolean(), nullable=True))

def downgrade():
    op.drop_column('point', 'deleted_by_user')
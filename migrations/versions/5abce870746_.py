"""empty message

Revision ID: 5abce870746
Revises: 5457410e2a4
Create Date: 2015-12-18 14:42:27.760292

"""

# revision identifiers, used by Alembic.
revision = '5abce870746'
down_revision = '5457410e2a4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('point', sa.Column('image', sa.String))


def downgrade():
    op.drop_column('point', 'image')
"""empty message

Revision ID: 1de17aaff3
Revises: 499bc5f2a82
Create Date: 2015-07-12 13:35:30.109224

"""

# revision identifiers, used by Alembic.
revision = '1de17aaff3'
down_revision = '499bc5f2a82'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('point', sa.Column('revised', sa.Boolean, server_default='FALSE'))
    op.add_column('point', sa.Column('submission_id', sa.String))


def downgrade():
    op.drop_column('point', 'revised')
    op.drop_column('point', 'submission_id')

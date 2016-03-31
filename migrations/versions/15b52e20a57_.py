"""empty message

Revision ID: 15b52e20a57
Revises: 245a2ea2ba
Create Date: 2016-03-12 19:07:44.053784

"""

# revision identifiers, used by Alembic.
revision = '15b52e20a57'
down_revision = '245a2ea2ba'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('point', sa.Column('merged_to', sa.Integer, nullable=True))


def downgrade():
    op.drop_column('point', 'merged_to')
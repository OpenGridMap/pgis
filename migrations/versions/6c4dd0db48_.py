"""empty message

Revision ID: 6c4dd0db48
Revises: 15b52e20a57
Create Date: 2016-05-27 13:10:42.234436

"""

# revision identifiers, used by Alembic.
revision = '6c4dd0db48'
down_revision = '15b52e20a57'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('user', sa.Column('activity_points', sa.Integer(), server_default='0'))


def downgrade():
    op.drop_column('user', 'activity_points')
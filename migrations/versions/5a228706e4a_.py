"""empty message

Revision ID: 5a228706e4a
Revises: 58ba1b9ec53
Create Date: 2016-11-30 05:39:43.662561

"""

# revision identifiers, used by Alembic.
revision = '5a228706e4a'
down_revision = '21466a6ed49'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('ALTER TABLE "user" ALTER COLUMN activity_points TYPE numeric(7,1)')
    op.execute('ALTER TABLE "user" RENAME COLUMN activity_points to activity_points_total')
    op.add_column('user', sa.Column('activity_points', sa.Numeric(precision=7, scale=1), server_default='0.0'))



def downgrade():
    op.drop_column('user', 'activity_points')
    op.execute('ALTER TABLE "user" ALTER COLUMN activity_points TYPE integer')
    op.execute('ALTER TABLE "user" RENAME COLUMN activity_points_total to activity_points')
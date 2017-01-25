"""transnet_stat_name_fix

Revision ID: 184736d30fd
Revises: 559c59c46c2
Create Date: 2017-01-25 16:43:15.245411

"""

# revision identifiers, used by Alembic.
revision = '184736d30fd'
down_revision = '559c59c46c2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('ALTER TABLE "transnet_stats" RENAME COLUMN lat_update to last_updated')


def downgrade():
    op.execute('ALTER TABLE "transnet_stats" RENAME COLUMN last_updated to lat_update')

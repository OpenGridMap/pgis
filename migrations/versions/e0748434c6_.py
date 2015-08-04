"""empty message

Revision ID: e0748434c6
Revises: 2b9139423
Create Date: 2015-08-04 18:41:49.014171

"""

# revision identifiers, used by Alembic.
revision = 'e0748434c6'
down_revision = '2b9139423'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("CREATE INDEX osm_idx ON point((properties->>'osmid'))")


def downgrade():
    op.execute("DROP INDEX osm_idx")

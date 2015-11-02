"""empty message

Revision ID: 5457410e2a4
Revises: 20f9359b6cf
Create Date: 2015-10-30 15:10:09.532861

"""

# revision identifiers, used by Alembic.
revision = '5457410e2a4'
down_revision = '20f9359b6cf'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('ALTER TABLE submission ALTER COLUMN submission_id TYPE bigint')


def downgrade():
    op.execute('ALTER TABLE submission ALTER COLUMN submission_id TYPE integer')
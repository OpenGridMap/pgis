"""empty message

Revision ID: 20efc53357f
Revises: e0748434c6
Create Date: 2015-08-08 11:41:35.861799

"""

# revision identifiers, used by Alembic.
revision = '20efc53357f'
down_revision = 'e0748434c6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('ALTER TABLE point ALTER COLUMN submission_id TYPE integer USING (submission_id::integer)')


def downgrade():
    op.execute('ALTER TABLE point ALTER COLUMN submission_id TYPE varchar(50) USING (submission_id::varchar)')

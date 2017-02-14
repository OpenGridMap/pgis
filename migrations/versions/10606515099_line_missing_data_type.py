"""line_missing_data_type

Revision ID: 10606515099
Revises: 4153975f210
Create Date: 2017-02-02 14:59:29.685404

"""

# revision identifiers, used by Alembic.
revision = '10606515099'
down_revision = '4153975f210'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('transnet_line_missing_data', sa.Column('type', sa.String(), nullable=True))


def downgrade():
    op.drop_column('transnet_line_missing_data', 'type')

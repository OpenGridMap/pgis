"""transnet_stat

Revision ID: 559c59c46c2
Revises: 5a228706e4a
Create Date: 2017-01-25 16:34:30.507453

"""

# revision identifiers, used by Alembic.
revision = '559c59c46c2'
down_revision = '5a228706e4a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('transnet_stats',
                    sa.Column('id', sa.Integer, nullable=False),
                    sa.Column('lat_update', sa.Date, nullable=False),
                    sa.PrimaryKeyConstraint('id'))


def downgrade():
    op.drop_table('transnet_stats')

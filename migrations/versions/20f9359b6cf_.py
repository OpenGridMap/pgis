"""empty message

Revision ID: 20f9359b6cf
Revises: 20efc53357f
Create Date: 2015-08-10 19:09:38.651927

"""

# revision identifiers, used by Alembic.
revision = '20f9359b6cf'
down_revision = '20efc53357f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('submission', 'point_data')
    op.add_column('submission', sa.Column('number_of_points', sa.Integer ))


def downgrade():
    op.drop_column('submission', 'number_of_points')
    op.add_column('submission', sa.Column('point_data', JSON))


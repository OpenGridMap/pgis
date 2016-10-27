"""renaming country voltage to voltages

Revision ID: d95ebf6984
Revises: 3a359e6c77d
Create Date: 2016-10-06 17:37:57.369767

"""

# revision identifiers, used by Alembic.
revision = 'd95ebf6984'
down_revision = '3a359e6c77d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('ALTER TABLE transnet_country RENAME COLUMN voltage TO voltages')


def downgrade():
    op.execute('ALTER TABLE transnet_country RENAME COLUMN voltages TO voltage')

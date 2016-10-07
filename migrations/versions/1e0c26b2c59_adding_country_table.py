"""adding country table

Revision ID: 1e0c26b2c59
Revises: 1664b06a80a
Create Date: 2016-10-06 17:08:39.257831

"""

# revision identifiers, used by Alembic.
revision = '1e0c26b2c59'
down_revision = '1664b06a80a'

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


def upgrade():
    op.create_table('transnet_country',
                    sa.Column('id', sa.Integer, nullable=False),
                    sa.Column('country', sa.String(), nullable=False),
                    sa.Column('continent', sa.String(), nullable=False),
                    sa.Column('voltage', postgresql.ARRAY(sa.INTEGER()), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('transnet_country')

"""empty message

Revision ID: 201b7349c89
Revises: 3f088e2050e
Create Date: 2016-09-23 13:06:33.474628

"""

# revision identifiers, used by Alembic.
revision = '201b7349c89'
down_revision = '3f088e2050e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.create_table('transnet_relation',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('country', sa.String(), nullable=True),
                    sa.Column('ref', sa.String(), nullable=True),
                    sa.Column('voltage', postgresql.ARRAY(sa.INTEGER()), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('transnet_relation')

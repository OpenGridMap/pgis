"""user_export

Revision ID: 33c165958d2
Revises: 184736d30fd
Create Date: 2017-01-26 13:24:37.817607

"""

# revision identifiers, used by Alembic.
revision = '33c165958d2'
down_revision = '184736d30fd'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.create_table('transnet_download_user',
                    sa.Column('id', sa.Integer, nullable=False),
                    sa.Column('uuid', sa.String, nullable=False),
                    sa.Column('name', sa.String, nullable=False),
                    sa.Column('organization', sa.String, nullable=False),
                    sa.Column('purpose', sa.String, nullable=False),
                    sa.Column('email', sa.String, nullable=True),
                    sa.Column('url', sa.String, nullable=True),
                    sa.Column('created', sa.Date, nullable=False),
                    sa.PrimaryKeyConstraint('id'))


def downgrade():
    op.drop_table('transnet_download_user')

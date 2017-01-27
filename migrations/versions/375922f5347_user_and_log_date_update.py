"""user_and_log_date_update

Revision ID: 375922f5347
Revises: a8b5cee1f8
Create Date: 2017-01-26 16:57:46.067706

"""

# revision identifiers, used by Alembic.
revision = '375922f5347'
down_revision = 'a8b5cee1f8'

from alembic import op
import sqlalchemy as sa
from datetime import datetime


def upgrade():
    now = datetime.now()
    op.drop_column('transnet_download_log', 'created')
    op.drop_column('transnet_download_user', 'created')
    op.add_column('transnet_download_log', sa.Column('created', sa.DateTime, default=now))
    op.add_column('transnet_download_user', sa.Column('created', sa.DateTime, default=now))


def downgrade():
    now = datetime.now()
    op.drop_column('transnet_download_log', 'created')
    op.drop_column('transnet_download_user', 'created')
    op.add_column('transnet_download_log', sa.Column('created', sa.DateTime, default=now))
    op.add_column('transnet_download_user', sa.Column('created', sa.DateTime, default=now))

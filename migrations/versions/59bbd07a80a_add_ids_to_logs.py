"""add_ids_to_logs

Revision ID: 59bbd07a80a
Revises: 375922f5347
Create Date: 2017-01-26 17:26:56.855145

"""

# revision identifiers, used by Alembic.
revision = '59bbd07a80a'
down_revision = '375922f5347'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('transnet_download_log', sa.Column('relations_ids', sa.String,))


def downgrade():
    op.drop_column('transnet_download_log', 'relations_ids')

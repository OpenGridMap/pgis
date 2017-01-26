"""user_export_logs

Revision ID: a8b5cee1f8
Revises: 33c165958d2
Create Date: 2017-01-26 16:08:27.326548

"""

# revision identifiers, used by Alembic.
revision = 'a8b5cee1f8'
down_revision = '33c165958d2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('transnet_download_log',
                    sa.Column('id', sa.Integer, nullable=False),
                    sa.Column('bounds', sa.String, nullable=True),
                    sa.Column('countries', sa.String, nullable=True),
                    sa.Column('voltages', sa.String, nullable=True),
                    sa.Column('type', sa.String, nullable=True),
                    sa.Column('download_user_id', sa.INTEGER, nullable=True),
                    sa.Column('created', sa.Date, nullable=False),
                    sa.ForeignKeyConstraint(['download_user_id'], ['transnet_download_user.id'], ),
                    sa.PrimaryKeyConstraint('id'))


def downgrade():
    op.drop_table('transnet_download_log')

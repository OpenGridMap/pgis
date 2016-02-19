"""empty message

Revision ID: 13d7ddfddbc
Revises: 1de17aaff3
Create Date: 2015-07-22 10:32:05.635884

"""

# revision identifiers, used by Alembic.
revision = '13d7ddfddbc'
down_revision = '1de17aaff3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


def upgrade():
    op.create_table('submission',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('submission_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('point_data', JSON),
    sa.Column('revised', sa.Boolean, server_default='FALSE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_submission_submission_id'), 'submission', ['submission_id'])
    op.create_index(op.f('ix_submission_user_id'), 'submission', ['user_id'])


def downgrade():
    op.drop_table('submission')
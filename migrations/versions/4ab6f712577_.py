"""empty message

Revision ID: 4ab6f712577
Revises: 5abce870746
Create Date: 2016-01-29 17:18:25.398896

"""

# revision identifiers, used by Alembic.
revision = '4ab6f712577'
down_revision = '5abce870746'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('point', sa.Column('approved', sa.Boolean, server_default='FALSE'))
    op.add_column('submission', sa.Column('approved', sa.Boolean, server_default='FALSE'))
    op.execute('UPDATE point SET approved = TRUE WHERE revised = TRUE')
    op.execute('UPDATE submission SET approved = TRUE WHERE revised = TRUE')


def downgrade():
    op.drop_column('point', 'approved')
    op.drop_column('submission', 'approved')
"""empty message

Revision ID: 29c4a532deb
Revises: 48782e886c1
Create Date: 2015-03-17 01:29:01.812802

"""

# revision identifiers, used by Alembic.
revision = '29c4a532deb'
down_revision = '48782e886c1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('user', sa.Column('email', sa.String))
    op.add_column('user', sa.Column('password', sa.String))
    op.add_column('user', sa.Column('authenticated', sa.Boolean, server_default='FALSE'))


def downgrade():
    op.drop_column('user', 'email')
    op.drop_column('user', 'password') 
    op.drop_column('user', 'authenticated')

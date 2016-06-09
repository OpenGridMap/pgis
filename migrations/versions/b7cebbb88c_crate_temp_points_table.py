"""crate temp_points table

Revision ID: b7cebbb88c
Revises: 9aaa71af05
Create Date: 2016-06-09 11:49:56.571567

"""

# revision identifiers, used by Alembic.
revision = 'b7cebbb88c'
down_revision = '9aaa71af05'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


def upgrade():
    # copy the structure of `point` table and create `temp_points`
    # Note: The below approach won't copy quite some information like
    #       Foreignkeys and triggers.
    #       Refer: http://stackoverflow.com/a/1220942/976880
    op.execute("CREATE table temp_points("\
                   "like point "\
                   "including defaults "\
                   "including constraints "\
                   "including indexes"\
               ")")


def downgrade():
    op.drop_table("temp_points")

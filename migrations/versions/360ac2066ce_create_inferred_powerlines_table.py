"""create inferred_powerlines table

Revision ID: 360ac2066ce
Revises: 58ba1b9ec53
Create Date: 2016-08-28 14:40:35.960705

"""

# revision identifiers, used by Alembic.
revision = '360ac2066ce'
down_revision = '58ba1b9ec53'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # copy the structure of `powerline` table and create `inferred_powerlines`
    # Note: The below approach won't copy quite some information like
    #       Foreignkeys and triggers.
    #       Refer: http://stackoverflow.com/a/1220942/976880
    op.execute("CREATE table inferred_powerlines("\
                   "like powerline "\
                   "including defaults "\
                   "including constraints "\
                   "including indexes"\
               ")")

def downgrade():
    op.drop_table("inferred_powerlines")

"""many to many relations

Revision ID: 564d4b52ea2
Revises: 566d8ab0906
Create Date: 2016-10-26 10:52:46.031141

"""

# revision identifiers, used by Alembic.
revision = '564d4b52ea2'
down_revision = '566d8ab0906'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.create_table('transnet_relation_station',
                    sa.Column('relation_id', sa.Integer(), nullable=False),
                    sa.Column('station_id', sa.Integer(), nullable=False),
                    sa.Column('country', sa.String(), nullable=True),
                    sa.ForeignKeyConstraint(['relation_id'], ['transnet_relation.id'], ),
                    sa.ForeignKeyConstraint(['station_id'], ['transnet_station.id'], ),
                    sa.PrimaryKeyConstraint('relation_id', 'station_id'))

    op.create_table('transnet_relation_powerline',
                    sa.Column('relation_id', sa.Integer(), nullable=False),
                    sa.Column('powerline_id', sa.Integer(), nullable=False),
                    sa.Column('country', sa.String(), nullable=True),
                    sa.ForeignKeyConstraint(['relation_id'], ['transnet_relation.id'], ),
                    sa.ForeignKeyConstraint(['powerline_id'], ['transnet_powerline.id'], ),
                    sa.PrimaryKeyConstraint('relation_id', 'powerline_id'))


def downgrade():
    op.drop_table('transnet_relation_station')
    op.drop_table('transnet_relation_powerline')

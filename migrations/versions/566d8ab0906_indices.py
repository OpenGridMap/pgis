"""indices

Revision ID: 566d8ab0906
Revises: d95ebf6984
Create Date: 2016-10-20 13:25:35.758270

"""

# revision identifiers, used by Alembic.
revision = '566d8ab0906'
down_revision = 'd95ebf6984'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index(op.f('ix_transnet_relation_country'), 'transnet_relation', ['country'])
    op.create_index(op.f('ix_transnet_station_country'), 'transnet_station', ['country'])
    op.create_index(op.f('ix_transnet_line_country'), 'transnet_powerline', ['country'])

    op.create_index(op.f('ix_transnet_relation_voltage'), 'transnet_relation', ['voltage'])
    op.create_index(op.f('ix_transnet_station_voltage'), 'transnet_station', ['voltage'])
    op.create_index(op.f('ix_transnet_line_voltage'), 'transnet_powerline', ['voltage'])


def downgrade():
    op.drop_index(op.f('ix_transnet_relation_country'), table_name='transnet_relation')
    op.drop_index(op.f('ix_transnet_station_country'), table_name='transnet_station')
    op.drop_index(op.f('ix_transnet_line_country'), table_name='transnet_powerline')

    op.drop_index(op.f('ix_transnet_relation_voltage'), table_name='transnet_relation')
    op.drop_index(op.f('ix_transnet_station_voltage'), table_name='transnet_station')
    op.drop_index(op.f('ix_transnet_line_voltage'), table_name='transnet_powerline')

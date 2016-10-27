"""scigrid

Revision ID: e5558f7f27
Revises: 340badbcba6
Create Date: 2016-10-27 12:23:20.818930

"""

# revision identifiers, used by Alembic.
import geoalchemy2
from sqlalchemy.dialects import postgresql

revision = 'e5558f7f27'
down_revision = '340badbcba6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('scigrid_powerline',
                    sa.Column('id', sa.Integer, nullable=False),
                    sa.Column('l_id', sa.Integer, nullable=True),
                    sa.Column('v_id_1', sa.Integer, nullable=True),
                    sa.Column('v_id_2', sa.Integer, nullable=True),
                    sa.Column('voltage', postgresql.ARRAY(sa.INTEGER()), nullable=True),
                    sa.Column('cables', postgresql.ARRAY(sa.INTEGER()), nullable=True),
                    sa.Column('wires', postgresql.ARRAY(sa.INTEGER()), nullable=True),
                    sa.Column('frequency', postgresql.ARRAY(sa.INTEGER()), nullable=True),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.Column('operator', sa.String(), nullable=True),
                    sa.Column('ref', sa.String(), nullable=True),
                    sa.Column('length_m', sa.NUMERIC(), nullable=True),
                    sa.Column('r_ohmkm', sa.NUMERIC(), nullable=True),
                    sa.Column('x_ohmkm', sa.NUMERIC(), nullable=True),
                    sa.Column('c_nfkm', sa.NUMERIC(), nullable=True),
                    sa.Column('i_th_max_a', sa.NUMERIC(), nullable=True),
                    sa.Column('from_relation', sa.BOOLEAN(), nullable=True),
                    sa.Column('geom', geoalchemy2.types.Geometry(geometry_type='LINESTRING'), nullable=True),
                    sa.PrimaryKeyConstraint('id'))

    op.create_table('scigrid_station',
                    sa.Column('id', sa.Integer, nullable=False),
                    sa.Column('v_id', sa.Integer, nullable=True),
                    sa.Column('lon', sa.NUMERIC(), nullable=True),
                    sa.Column('lat', sa.NUMERIC(), nullable=True),
                    sa.Column('type', sa.String(), nullable=True),
                    sa.Column('voltage', postgresql.ARRAY(sa.INTEGER()), nullable=True),
                    sa.Column('frequency', postgresql.ARRAY(sa.INTEGER()), nullable=True),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.Column('operator', sa.String(), nullable=True),
                    sa.Column('ref', sa.String(), nullable=True),
                    sa.Column('geom', geoalchemy2.types.Geometry(geometry_type='POINT'), nullable=True),
                    sa.PrimaryKeyConstraint('id'))


def downgrade():
    op.drop_table('scigrid_powerline')
    op.drop_table('scigird_station')

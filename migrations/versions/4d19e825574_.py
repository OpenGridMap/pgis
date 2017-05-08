"""empty message

Revision ID: 4d19e825574
Revises: 306abdb215f
Create Date: 2017-05-04 21:26:29.667332

"""

# revision identifiers, used by Alembic.
revision = '4d19e825574'
down_revision = '306abdb215f'

import geoalchemy2
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('crowdsourcing_polygon',
                    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('geom', geoalchemy2.types.Geometry(geometry_type='POLYGON'), nullable=False)
                    )


def downgrade():
    op.drop_table('crowdsourcing_polygon')
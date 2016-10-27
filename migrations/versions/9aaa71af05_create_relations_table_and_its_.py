"""create relations table and its plymorphic join table

Revision ID: 9aaa71af05
Revises: 15b52e20a57
Create Date: 2016-06-05 11:50:32.377423

"""

# revision identifiers, used by Alembic.
revision = '9aaa71af05'
down_revision = '15b52e20a57'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

def upgrade():
    op.create_table('power_relations',
            sa.Column('id', sa.Integer, nullable=False),
            sa.PrimaryKeyConstraint('id')
            )
    op.add_column('power_relations', sa.Column('properties', JSON))
    op.execute("CREATE INDEX power_relations_osm_idx ON power_relations((properties->>'osmid'))")

    op.create_table('power_relation_members',
            sa.Column('id', sa.Integer, nullable=False),
            sa.Column('power_relation_id', sa.Integer, nullable=False),
            sa.Column('member_id', sa.Integer, nullable=False),
            sa.Column('member_osm_id', sa.String(length=64), nullable=True),
            sa.Column('member_type', sa.String(length=64), nullable=False),
            sa.Column('member_role', sa.String(length=64), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['power_relation_id'], ['power_relations.id']))
    op.execute("CREATE INDEX power_relations_members_osm_idx ON power_relation_members(member_osm_id)")

def downgrade():
    op.execute("DROP INDEX power_relations_osm_idx")
    op.execute("DROP INDEX power_relations_members_osm_idx")
    op.drop_table('power_relation_members')
    op.drop_table('power_relations')

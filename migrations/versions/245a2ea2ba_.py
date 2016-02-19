"""empty message

Revision ID: 245a2ea2ba
Revises: 4ab6f712577
Create Date: 2016-02-19 17:09:48.885139

"""

# revision identifiers, used by Alembic.
revision = '245a2ea2ba'
down_revision = '4ab6f712577'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('picture',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('point_id', sa.Integer(), nullable=False),
    sa.Column('submission_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('filepath', sa.String, nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_picture_point_id'), 'picture', ['point_id'])
    op.execute('INSERT INTO picture (point_id, submission_id, user_id, filepath) SELECT point.id AS point_id, point.submission_id AS submission_id, "user".id as user_id, point.image AS filepath FROM point JOIN submission on point.submission_id = submission.id JOIN "user" on submission.user_id = "user".id where point.image IS NOT NULL AND point.submission_id IS NOT NULL')
    op.drop_column('point', 'image')


def downgrade():
    op.add_column('point', sa.Column('image', sa.String))
    op.execute('UPDATE point SET image = picture.filepath FROM picture WHERE picture.point_id = point.id')
    op.drop_table('picture')
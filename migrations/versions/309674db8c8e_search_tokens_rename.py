"""search tokens rename

Revision ID: 309674db8c8e
Revises: c37cdff15ad1
Create Date: 2021-04-28 21:29:14.104364

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '309674db8c8e'
down_revision = 'c37cdff15ad1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token')
    )
    op.drop_table('tokens')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tokens',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('token', sa.VARCHAR(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token')
    )
    op.drop_table('token')
    # ### end Alembic commands ###
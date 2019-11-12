"""Add in table user field is_admin

Revision ID: 698390eb4c9a
Revises: e0ff4bb659d9
Create Date: 2019-11-10 19:51:59.613790

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '698390eb4c9a'
down_revision = 'e0ff4bb659d9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('is_admin', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'is_admin')
    # ### end Alembic commands ###
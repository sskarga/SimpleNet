"""add table client log

Revision ID: 76f31dce8c82
Revises: e4bead470924
Create Date: 2019-10-29 22:14:58.154605

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76f31dce8c82'
down_revision = 'e4bead470924'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('log_client',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_id', sa.Integer(), nullable=True),
    sa.Column('initiator_id', sa.Integer(), nullable=True),
    sa.Column('create_at', sa.DateTime(), nullable=True),
    sa.Column('type', sa.String(length=1), nullable=True),
    sa.Column('event', sa.String(length=250), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('_eqpt_old_20191023')
    op.add_column('client', sa.Column('suspension_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('client', 'suspension_at')
    op.create_table('_eqpt_old_20191023',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), nullable=True),
    sa.Column('building_id', sa.INTEGER(), nullable=True),
    sa.Column('ip', sa.INTEGER(), nullable=True),
    sa.Column('serial', sa.VARCHAR(length=50), nullable=True),
    sa.Column('mac', sa.VARCHAR(length=20), nullable=True),
    sa.Column('note', sa.VARCHAR(length=200), nullable=True),
    sa.Column('network_id', sa.INTEGER(), nullable=True),
    sa.Column('model_id', sa.INTEGER(), nullable=True),
    sa.Column('cvlan', sa.INTEGER(), nullable=True),
    sa.Column('inc_cvlan', sa.BOOLEAN(), nullable=True),
    sa.ForeignKeyConstraint(['model_id'], ['eqptmodel.id'], onupdate='NO ACTION', ondelete='NO ACTION'),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('log_client')
    # ### end Alembic commands ###

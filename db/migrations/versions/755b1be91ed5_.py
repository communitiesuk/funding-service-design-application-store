"""empty message

Revision ID: 755b1be91ed5
Revises: 
Create Date: 2022-08-15 16:55:27.754731

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlalchemy_utils

# revision identifiers, used by Alembic.
revision = '755b1be91ed5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('applications',
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
    sa.Column('account_id', sa.String(), nullable=False),
    sa.Column('round_id', sa.String(), nullable=False),
    sa.Column('fund_id', sa.String(), nullable=False),
    sa.Column('project_name', sa.String(), nullable=True),
    sa.Column('started_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('status', postgresql.ENUM('NOT_STARTED', 'IN_PROGRESS', 'SUBMITTED', 'COMPLETED', name='status'), nullable=False),
    sa.Column('date_submitted', sa.DateTime(), nullable=True),
    sa.Column('last_edited', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_applications'))
    )
    op.create_table('forms',
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
    sa.Column('application_id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
    sa.Column('json', sa.JSON(), nullable=True),
    sa.Column('status', sa.Enum('NOT_STARTED', 'IN_PROGRESS', 'SUBMITTED', 'COMPLETED', name='status'), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['application_id'], ['applications.id'], name=op.f('fk_forms_application_id_applications')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_forms')),
    sa.UniqueConstraint('id', 'name', name=op.f('uq_forms_id'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('forms')
    op.drop_table('applications')
    # ### end Alembic commands ###
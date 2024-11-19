"""empty message

Revision ID: 4a40deca2d61
Revises: eb61bc354c57
Create Date: 2024-11-19 18:51:54.942195

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4a40deca2d61"
down_revision = "eb61bc354c57"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE status ADD VALUE 'CHANGES_REQUESTED'")

    with op.batch_alter_table("forms", schema=None) as batch_op:
        batch_op.add_column(sa.Column("feedback_message", sa.String(), nullable=True))


def downgrade():
    # remove CHANGES_REQUESTED from the status enum is a bit harder

    with op.batch_alter_table("forms", schema=None) as batch_op:
        batch_op.drop_column("feedback_message")

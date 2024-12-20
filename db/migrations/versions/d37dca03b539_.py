"""empty message

Revision ID: d37dca03b539
Revises: f524201314e9
Create Date: 2024-01-29 10:28:40.018763

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d37dca03b539"
down_revision = "f524201314e9"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "eligibility_update",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "date_created",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("eligible", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_eligibility_update")),
    )
    op.create_table(
        "eligibility",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("form_id", sa.String(), nullable=False),
        sa.Column("answers", sa.JSON(), nullable=True),
        sa.Column("eligible", sa.Boolean(), nullable=True),
        sa.Column("application_id", sa.UUID(), nullable=False),
        sa.Column("date_submitted", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["application_id"],
            ["applications.id"],
            name=op.f("fk_eligibility_application_id_applications"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_eligibility")),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("eligibility")
    op.drop_table("eligibility_update")
    # ### end Alembic commands ###

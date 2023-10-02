"""add model entity [3b68abe58f44].

Revision ID: 3b68abe58f44
Revises: 0.44.2
Create Date: 2023-09-11 07:53:18.641081

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "3b68abe58f44"
down_revision = "0.44.3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema and/or data, creating a new revision."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "model",
        sa.Column(
            "workspace_id", sqlmodel.sql.sqltypes.GUID(), nullable=False
        ),
        sa.Column("user_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column("license", sa.TEXT(), nullable=True),
        sa.Column("description", sa.TEXT(), nullable=True),
        sa.Column("audience", sa.TEXT(), nullable=True),
        sa.Column("use_cases", sa.TEXT(), nullable=True),
        sa.Column("limitations", sa.TEXT(), nullable=True),
        sa.Column("trade_offs", sa.TEXT(), nullable=True),
        sa.Column("ethic", sa.TEXT(), nullable=True),
        sa.Column("tags", sa.TEXT(), nullable=True),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name="fk_model_user_id_user",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspace.id"],
            name="fk_model_workspace_id_workspace",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade database schema and/or data back to the previous revision."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("model")
    # ### end Alembic commands ###

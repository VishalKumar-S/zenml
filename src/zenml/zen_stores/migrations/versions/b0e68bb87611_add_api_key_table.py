"""add api key table [b0e68bb87611].

Revision ID: b0e68bb87611
Revises: 47f55c2589f6
Create Date: 2023-09-20 16:54:02.154481

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "b0e68bb87611"
down_revision = "47f55c2589f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema and/or data, creating a new revision."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "api_key",
        sa.Column(
            "workspace_id", sqlmodel.sql.sqltypes.GUID(), nullable=False
        ),
        sa.Column("user_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "description", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("key", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "previous_key", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("retain_period", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("last_used", sa.DateTime(), nullable=False),
        sa.Column("last_rotated", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name="fk_api_key_user_id_user",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspace.id"],
            name="fk_api_key_workspace_id_workspace",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade database schema and/or data back to the previous revision."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("api_key")
    # ### end Alembic commands ###
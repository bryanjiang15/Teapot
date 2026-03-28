"""Add compilation fields to components (Kind, Script, Properties, EventSubscriptions).

Revision ID: f8a2c1d9e4b0
Revises: e730fee1cfe3
Create Date: 2026-03-23

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "f8a2c1d9e4b0"
down_revision = "e730fee1cfe3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("components", sa.Column("Kind", sa.String(length=50), nullable=True))
    op.add_column("components", sa.Column("Script", sa.Text(), nullable=True))
    op.add_column(
        "components",
        sa.Column("Properties", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "components",
        sa.Column(
            "EventSubscriptions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column("components", "EventSubscriptions")
    op.drop_column("components", "Properties")
    op.drop_column("components", "Script")
    op.drop_column("components", "Kind")

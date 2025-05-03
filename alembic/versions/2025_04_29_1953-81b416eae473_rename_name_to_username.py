"""rename_name_to_username

Revision ID: 81b416eae473
Revises: b6d7f721fe83
Create Date: 2025-04-29 19:53:06.188171

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "81b416eae473"
down_revision: Union[str, None] = "b6d7f721fe83"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "name",
        new_column_name="username",
        existing_type=sa.String(50),
        nullable=False
    )
    op.drop_constraint("users_name_key", "users", type_="unique")
    op.create_unique_constraint("uq_users_username", "users", ["username"])

def downgrade() -> None:
    op.alter_column(
        "users",
        "username",
        new_column_name="name",
        existing_type=sa.String(50),
        nullable=False
    )
    op.drop_constraint("uq_users_username", "users", type_="unique")
    op.create_unique_constraint("users_name_key", "users", ["name"])

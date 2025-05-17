"""merging heads

Revision ID: 388b481751a1
Revises: de43d9e27305, 34bdb57b0d31
Create Date: 2025-04-28 09:22:54.636587

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "388b481751a1"
down_revision: Union[str, None] = ("de43d9e27305", "34bdb57b0d31")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

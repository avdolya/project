"""remove_image_mimetype

Revision ID: 5a17200660a2
Revises: c3f79c33c2b4
Create Date: 2025-05-13 01:09:23.956302

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5a17200660a2"
down_revision: Union[str, None] = "c3f79c33c2b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_column('places', 'image_mimetype')

def downgrade():
    op.add_column('places', sa.Column('image_mimetype', sa.String(50)))
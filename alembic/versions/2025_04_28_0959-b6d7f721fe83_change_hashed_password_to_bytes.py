"""change_hashed_password_to_bytes

Revision ID: b6d7f721fe83
Revises: 388b481751a1
Create Date: 2025-04-28 09:59:00.058896

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b6d7f721fe83"
down_revision: Union[str, None] = "388b481751a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.alter_column('users', 'hashed_password',
                   type_=sa.LargeBinary(),
                   existing_type=sa.String(128),
                   postgresql_using='hashed_password::bytea')  # Конвертируем существующие данные

def downgrade():
    op.alter_column('users', 'hashed_password',
                   type_=sa.String(128),
                   existing_type=sa.LargeBinary(),
                   postgresql_using='encode(hashed_password, \'escape\')')

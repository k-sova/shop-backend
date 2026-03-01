"""add reviews check range grade

Revision ID: 477ffc083c40
Revises: d7343d592914
Create Date: 2026-03-01 14:24:53.540651

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '477ffc083c40'
down_revision: Union[str, Sequence[str], None] = 'd7343d592914'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_check_constraint(
        "check_grade_range",
        "reviews",
        "grade >= 1 AND grade <= 5"
    )

def downgrade():
    op.drop_constraint(
        "check_grade_range",
        "reviews",
        type_="check"
    )
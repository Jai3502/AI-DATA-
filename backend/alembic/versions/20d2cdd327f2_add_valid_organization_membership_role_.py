"""add valid organization membership role constraint"""
from typing import Sequence, Union
from alembic import op

revision: str = "20d2cdd327f2"
down_revision: Union[str, Sequence[str], None] = "b5c4774044cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_check_constraint(
        "ck_organization_memberships_valid_role",
        "organization_memberships",
        "role IN (\'owner\', \'admin\', \'analyst\', \'viewer\')",
    )

def downgrade() -> None:
    op.drop_constraint(
        "ck_organization_memberships_valid_role",
        "organization_memberships",
        type_="check",
    )

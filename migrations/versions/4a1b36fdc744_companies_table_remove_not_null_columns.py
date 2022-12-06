"""companies table: remove not_null columns

Revision ID: 4a1b36fdc744
Revises: e71c1cb14e28
Create Date: 2022-10-26 19:08:24.005252

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "4a1b36fdc744"
down_revision = "e71c1cb14e28"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "companies",
        "business_sector",
        existing_type=mysql.VARCHAR(
            charset="utf8mb4", collation="utf8mb4_0900_ai_ci", length=100
        ),
        nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "companies",
        "business_sector",
        existing_type=mysql.VARCHAR(
            charset="utf8mb4", collation="utf8mb4_0900_ai_ci", length=100
        ),
        nullable=True,
    )
    # ### end Alembic commands ###

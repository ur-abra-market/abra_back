"""add serial_number column to CompanyImages

Revision ID: ba3625b16d0b
Revises: 279b2b74b836
Create Date: 2022-11-28 18:46:37.185499

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ba3625b16d0b"
down_revision = "279b2b74b836"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "company_images", sa.Column("serial_number", sa.Integer(), nullable=False)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("company_images", "serial_number")
    # ### end Alembic commands ###
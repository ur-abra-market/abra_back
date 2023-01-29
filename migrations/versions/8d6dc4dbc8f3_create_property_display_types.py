"""Create property_display_types

Revision ID: 8d6dc4dbc8f3
Revises: ba3625b16d0b
Create Date: 2023-01-19 19:11:51.907078

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d6dc4dbc8f3'
down_revision = 'ba3625b16d0b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('property_display_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category_property_type_id', sa.Integer(), nullable=False),
    sa.Column('dropdown', sa.String(length=30), nullable=True),
    sa.Column('tiles', sa.String(length=15), nullable=True),
    sa.ForeignKeyConstraint(['category_property_type_id'], ['category_property_types.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('property_display_types')
    # ### end Alembic commands ###
"""Create price_schemas model

Revision ID: 1c43f4e98523
Revises: 84d9e84ec267
Create Date: 2022-09-17 18:18:09.737898

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1c43f4e98523'
down_revision = '84d9e84ec267'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('price_schemas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_price_id', sa.Integer(), nullable=False),
    sa.Column('value', sa.DECIMAL(precision=19, scale=4), nullable=False),
    sa.Column('min_quantity', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['product_price_id'], ['product_prices.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('price_schemas')
    # ### end Alembic commands ###

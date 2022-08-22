"""major structure changes

Revision ID: 8a55aaf026fa
Revises: 0b6d6a28b648
Create Date: 2022-08-22 22:38:22.094700

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8a55aaf026fa'
down_revision = '0b6d6a28b648'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_addresses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('country', sa.String(length=30), nullable=True),
    sa.Column('area', sa.String(length=50), nullable=True),
    sa.Column('city', sa.String(length=50), nullable=True),
    sa.Column('street', sa.String(length=100), nullable=True),
    sa.Column('building', sa.String(length=20), nullable=True),
    sa.Column('appartment', sa.String(length=20), nullable=True),
    sa.Column('postal_code', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('companies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('supplier_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('is_manufacturer', sa.Boolean(), nullable=True),
    sa.Column('year_established', sa.Integer(), nullable=True),
    sa.Column('number_of_employees', sa.Integer(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('buisness_email', sa.String(length=100), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('company_images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.Column('url', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('user_adresses')
    op.drop_column('suppliers', 'count')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('suppliers', sa.Column('count', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.create_table('user_adresses',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('country', mysql.VARCHAR(length=30), nullable=False),
    sa.Column('area', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('city', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('street', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('building', mysql.VARCHAR(length=20), nullable=False),
    sa.Column('appartment', mysql.VARCHAR(length=20), nullable=False),
    sa.Column('postal_code', mysql.VARCHAR(length=20), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='user_adresses_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('company_images')
    op.drop_table('companies')
    op.drop_table('user_addresses')
    # ### end Alembic commands ###

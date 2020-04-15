"""Add notifications

Revision ID: c8591a7abce5
Revises: 8bee00207b63
Create Date: 2020-03-11 18:08:51.709412

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c8591a7abce5"
down_revision = "8bee00207b63"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("notification", sa.String(), nullable=True))
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("is_ios")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("is_ios", sa.BOOLEAN(), nullable=True))
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("notification")
    # ### end Alembic commands ###
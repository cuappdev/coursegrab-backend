"""Add professors

Revision ID: 8bee00207b63
Revises: 6ce1a6f069ff
Create Date: 2020-03-08 21:48:22.794206

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8bee00207b63"
down_revision = "6ce1a6f069ff"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("sections", sa.Column("instructors", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("sections", "instructors")
    # ### end Alembic commands ###
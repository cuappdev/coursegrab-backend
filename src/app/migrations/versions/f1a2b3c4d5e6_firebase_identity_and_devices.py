"""Add Firebase identity and independent notification registrations.

Revision ID: f1a2b3c4d5e6
Revises: 3cfb8cf58e98
"""
from alembic import op
import sqlalchemy as sa

revision = "f1a2b3c4d5e6"
down_revision = "3cfb8cf58e98"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("firebase_uid", sa.String(128), nullable=True))
        batch.create_unique_constraint("uq_users_firebase_uid", ["firebase_uid"])
    op.create_table(
        "device_registrations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_type", sa.String(), nullable=False),
        sa.Column("device_token", sa.String(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("device_type", "device_token", name="uq_device_type_token"),
    )
    op.create_index("ix_device_registrations_user_id", "device_registrations", ["user_id"])
    # Existing device tokens remain in sessions and are read alongside v2 registrations.
    # Do not snapshot them: legacy clients can continue rotating tokens after deployment.


def downgrade():
    op.drop_table("device_registrations")
    with op.batch_alter_table("users") as batch:
        batch.drop_constraint("uq_users_firebase_uid", type_="unique")
        batch.drop_column("firebase_uid")

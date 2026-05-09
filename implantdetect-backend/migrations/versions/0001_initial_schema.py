"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-08

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(), nullable=False, unique=True),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False, server_default="user"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("active", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "label",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
    )

    op.create_table(
        "images",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("file_hash", sa.String(), nullable=False, unique=True),
        sa.Column("file_extension", sa.String(), nullable=True),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("active", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_index("ix_images_file_hash", "images", ["file_hash"])
    op.create_index("ix_images_user_id", "images", ["user_id"])

    op.create_table(
        "process",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("status", sa.Integer(), nullable=False),
        sa.Column("image_id", sa.Integer(), sa.ForeignKey("images.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_process_user_id", "process", ["user_id"])
    op.create_index("ix_process_image_id", "process", ["image_id"])

    op.create_table(
        "process_results",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "process_id", sa.Integer(), sa.ForeignKey("process.id"), nullable=False
        ),
        sa.Column("class_id", sa.Integer(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("bb_x1_center", sa.Float(), nullable=True),
        sa.Column("bb_y1_center", sa.Float(), nullable=True),
        sa.Column("bb_x2_center", sa.Float(), nullable=True),
        sa.Column("bb_y2_center", sa.Float(), nullable=True),
        sa.Column("bb_x3_center", sa.Float(), nullable=True),
        sa.Column("bb_y3_center", sa.Float(), nullable=True),
        sa.Column("bb_x4_center", sa.Float(), nullable=True),
        sa.Column("bb_y4_center", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("message", sa.String(), nullable=True),
    )
    op.create_index("ix_process_results_process_id", "process_results", ["process_id"])


def downgrade() -> None:
    op.drop_table("process_results")
    op.drop_table("process")
    op.drop_table("images")
    op.drop_table("label")
    op.drop_table("users")

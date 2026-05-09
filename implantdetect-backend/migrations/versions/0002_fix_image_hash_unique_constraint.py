"""fix image hash unique constraint

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-09

"""

from typing import Sequence, Union

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ix_images_file_hash was created as a unique index by create_all — drop and recreate as non-unique
    op.drop_index("ix_images_file_hash", table_name="images")
    op.create_index("ix_images_file_hash", "images", ["file_hash"])
    op.create_unique_constraint(
        "uq_image_hash_user", "images", ["file_hash", "user_id"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_image_hash_user", "images", type_="unique")
    op.drop_index("ix_images_file_hash", table_name="images")
    op.create_index("ix_images_file_hash", "images", ["file_hash"], unique=True)

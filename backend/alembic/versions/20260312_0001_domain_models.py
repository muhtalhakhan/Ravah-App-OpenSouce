"""Add founder content domain models and retire generic items flow.

Revision ID: 20260312_0001
Revises:
Create Date: 2026-03-12
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260312_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    if _table_exists("items"):
        op.drop_table("items")

    if not _table_exists("product_ideas"):
        op.create_table(
            "product_ideas",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("product_name", sa.String(length=200), nullable=False),
            sa.Column("short_description", sa.Text(), nullable=False),
            sa.Column("problem_statement", sa.Text(), nullable=True),
            sa.Column("target_audience", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_product_ideas_id"), "product_ideas", ["id"], unique=False)
        op.create_index(op.f("ix_product_ideas_product_name"), "product_ideas", ["product_name"], unique=False)
        op.create_index(op.f("ix_product_ideas_user_id"), "product_ideas", ["user_id"], unique=False)

    if not _table_exists("brand_profiles"):
        op.create_table(
            "brand_profiles",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("tone", sa.String(length=120), nullable=True),
            sa.Column("keywords", sa.JSON(), nullable=False),
            sa.Column("sample_post", sa.Text(), nullable=True),
            sa.Column("voice_guidelines", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id"),
        )
        op.create_index(op.f("ix_brand_profiles_id"), "brand_profiles", ["id"], unique=False)
        op.create_index(op.f("ix_brand_profiles_user_id"), "brand_profiles", ["user_id"], unique=True)

    if not _table_exists("brand_assets"):
        op.create_table(
            "brand_assets",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("brand_profile_id", sa.Integer(), nullable=True),
            sa.Column("source_type", sa.String(length=50), nullable=False),
            sa.Column("figma_file_url", sa.String(length=500), nullable=True),
            sa.Column("logo_url", sa.String(length=500), nullable=True),
            sa.Column("primary_color", sa.String(length=20), nullable=True),
            sa.Column("secondary_color", sa.String(length=20), nullable=True),
            sa.Column("typography", sa.String(length=200), nullable=True),
            sa.Column("metadata_json", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["brand_profile_id"], ["brand_profiles.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_brand_assets_brand_profile_id"), "brand_assets", ["brand_profile_id"], unique=False)
        op.create_index(op.f("ix_brand_assets_id"), "brand_assets", ["id"], unique=False)
        op.create_index(op.f("ix_brand_assets_user_id"), "brand_assets", ["user_id"], unique=False)

    if not _table_exists("content_plans"):
        op.create_table(
            "content_plans",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("product_idea_id", sa.Integer(), nullable=False),
            sa.Column("brand_profile_id", sa.Integer(), nullable=True),
            sa.Column("week_start", sa.Date(), nullable=False),
            sa.Column("platforms", sa.JSON(), nullable=False),
            sa.Column("weekly_themes", sa.JSON(), nullable=False),
            sa.Column("plan_notes", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=50), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["brand_profile_id"], ["brand_profiles.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["product_idea_id"], ["product_ideas.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_content_plans_brand_profile_id"), "content_plans", ["brand_profile_id"], unique=False)
        op.create_index(op.f("ix_content_plans_id"), "content_plans", ["id"], unique=False)
        op.create_index(op.f("ix_content_plans_product_idea_id"), "content_plans", ["product_idea_id"], unique=False)
        op.create_index(op.f("ix_content_plans_user_id"), "content_plans", ["user_id"], unique=False)

    if not _table_exists("content_posts"):
        op.create_table(
            "content_posts",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("content_plan_id", sa.Integer(), nullable=False),
            sa.Column("platform", sa.String(length=40), nullable=False),
            sa.Column("day_index", sa.Integer(), nullable=False),
            sa.Column("post_order", sa.Integer(), nullable=False),
            sa.Column("hook", sa.String(length=280), nullable=True),
            sa.Column("caption", sa.Text(), nullable=False),
            sa.Column("hashtags", sa.JSON(), nullable=False),
            sa.Column("visual_prompt", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=50), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["content_plan_id"], ["content_plans.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_content_posts_content_plan_id"), "content_posts", ["content_plan_id"], unique=False)
        op.create_index(op.f("ix_content_posts_id"), "content_posts", ["id"], unique=False)
        op.create_index(op.f("ix_content_posts_platform"), "content_posts", ["platform"], unique=False)
        op.create_index(op.f("ix_content_posts_user_id"), "content_posts", ["user_id"], unique=False)


def downgrade() -> None:
    if _table_exists("content_posts"):
        op.drop_index(op.f("ix_content_posts_user_id"), table_name="content_posts")
        op.drop_index(op.f("ix_content_posts_platform"), table_name="content_posts")
        op.drop_index(op.f("ix_content_posts_id"), table_name="content_posts")
        op.drop_index(op.f("ix_content_posts_content_plan_id"), table_name="content_posts")
        op.drop_table("content_posts")

    if _table_exists("content_plans"):
        op.drop_index(op.f("ix_content_plans_user_id"), table_name="content_plans")
        op.drop_index(op.f("ix_content_plans_product_idea_id"), table_name="content_plans")
        op.drop_index(op.f("ix_content_plans_id"), table_name="content_plans")
        op.drop_index(op.f("ix_content_plans_brand_profile_id"), table_name="content_plans")
        op.drop_table("content_plans")

    if _table_exists("brand_assets"):
        op.drop_index(op.f("ix_brand_assets_user_id"), table_name="brand_assets")
        op.drop_index(op.f("ix_brand_assets_id"), table_name="brand_assets")
        op.drop_index(op.f("ix_brand_assets_brand_profile_id"), table_name="brand_assets")
        op.drop_table("brand_assets")

    if _table_exists("brand_profiles"):
        op.drop_index(op.f("ix_brand_profiles_user_id"), table_name="brand_profiles")
        op.drop_index(op.f("ix_brand_profiles_id"), table_name="brand_profiles")
        op.drop_table("brand_profiles")

    if _table_exists("product_ideas"):
        op.drop_index(op.f("ix_product_ideas_user_id"), table_name="product_ideas")
        op.drop_index(op.f("ix_product_ideas_product_name"), table_name="product_ideas")
        op.drop_index(op.f("ix_product_ideas_id"), table_name="product_ideas")
        op.drop_table("product_ideas")

    if not _table_exists("items"):
        op.create_table(
            "items",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("owner_id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_items_id"), "items", ["id"], unique=False)
        op.create_index(op.f("ix_items_title"), "items", ["title"], unique=False)

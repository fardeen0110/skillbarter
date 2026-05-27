"""productize skillbarter domain

Revision ID: 20260517_000003
Revises: 20260503_000002
Create Date: 2026-05-17 00:00:03
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260517_000003"
down_revision = "20260503_000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("users", sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column(
        "users",
        sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("bio", sa.Text(), nullable=False, server_default=""),
        sa.Column("city", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("availability", sa.Text(), nullable=False, server_default=""),
        sa.Column("experience_level", sa.String(length=40), nullable=False, server_default="intermediate"),
        sa.Column("avatar_filename", sa.String(length=255), nullable=True),
        sa.Column("avatar_content_type", sa.String(length=120), nullable=True),
        sa.Column("avatar_data", sa.LargeBinary(), nullable=True),
        sa.Column("linkedin_url", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("website_url", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("x_url", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("rating_average", sa.Float(), nullable=False, server_default="0"),
        sa.Column("rating_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_user_profiles_id"), "user_profiles", ["id"], unique=False)
    op.create_index(op.f("ix_user_profiles_user_id"), "user_profiles", ["user_id"], unique=True)

    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=140), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False, server_default="general"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug", name="uq_skills_slug"),
    )
    op.create_index(op.f("ix_skills_id"), "skills", ["id"], unique=False)
    op.create_index(op.f("ix_skills_name"), "skills", ["name"], unique=True)
    op.create_index(op.f("ix_skills_slug"), "skills", ["slug"], unique=True)

    skills_table = sa.table(
        "skills",
        sa.column("name", sa.String(length=120)),
        sa.column("slug", sa.String(length=140)),
        sa.column("category", sa.String(length=80)),
    )
    op.bulk_insert(
        skills_table,
        [
            {"name": "React", "slug": "react", "category": "engineering"},
            {"name": "Python", "slug": "python", "category": "engineering"},
            {"name": "Node.js", "slug": "node-js", "category": "engineering"},
            {"name": "Figma", "slug": "figma", "category": "design"},
            {"name": "UI Design", "slug": "ui-design", "category": "design"},
            {"name": "Graphic Design", "slug": "graphic-design", "category": "design"},
            {"name": "Product Strategy", "slug": "product-strategy", "category": "product"},
            {"name": "Project Management", "slug": "project-management", "category": "product"},
            {"name": "Growth Marketing", "slug": "growth-marketing", "category": "marketing"},
            {"name": "SEO", "slug": "seo", "category": "marketing"},
            {"name": "Content Writing", "slug": "content-writing", "category": "marketing"},
            {"name": "Data Analysis", "slug": "data-analysis", "category": "analytics"},
            {"name": "SQL", "slug": "sql", "category": "analytics"},
            {"name": "Public Speaking", "slug": "public-speaking", "category": "communication"},
            {"name": "Pitch Decks", "slug": "pitch-decks", "category": "communication"},
            {"name": "Career Coaching", "slug": "career-coaching", "category": "coaching"},
            {"name": "No-Code Automation", "slug": "no-code-automation", "category": "automation"},
            {"name": "AI Workflow Design", "slug": "ai-workflow-design", "category": "automation"},
            {"name": "Video Editing", "slug": "video-editing", "category": "media"},
            {"name": "Motion Design", "slug": "motion-design", "category": "media"},
        ],
    )

    op.create_table(
        "user_offered_skills",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "skill_id", name="uq_user_offered_skill"),
    )
    op.create_index(op.f("ix_user_offered_skills_id"), "user_offered_skills", ["id"], unique=False)
    op.create_index(op.f("ix_user_offered_skills_skill_id"), "user_offered_skills", ["skill_id"], unique=False)
    op.create_index(op.f("ix_user_offered_skills_user_id"), "user_offered_skills", ["user_id"], unique=False)

    op.create_table(
        "user_wanted_skills",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "skill_id", name="uq_user_wanted_skill"),
    )
    op.create_index(op.f("ix_user_wanted_skills_id"), "user_wanted_skills", ["id"], unique=False)
    op.create_index(op.f("ix_user_wanted_skills_skill_id"), "user_wanted_skills", ["skill_id"], unique=False)
    op.create_index(op.f("ix_user_wanted_skills_user_id"), "user_wanted_skills", ["user_id"], unique=False)

    op.create_table(
        "follows",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("follower_id", sa.Integer(), nullable=False),
        sa.Column("followed_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["followed_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["follower_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("follower_id", "followed_id", name="uq_follow_pair"),
    )
    op.create_index(op.f("ix_follows_followed_id"), "follows", ["followed_id"], unique=False)
    op.create_index(op.f("ix_follows_follower_id"), "follows", ["follower_id"], unique=False)
    op.create_index(op.f("ix_follows_id"), "follows", ["id"], unique=False)

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("body", sa.Text(), nullable=False, server_default=""),
        sa.Column("link_url", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_id"), "notifications", ["id"], unique=False)
    op.create_index(op.f("ix_notifications_type"), "notifications", ["type"], unique=False)
    op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False)

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reviewer_id", sa.Integer(), nullable=False),
        sa.Column("reviewee_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False, server_default=""),
        sa.Column("endorsement", sa.String(length=160), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["reviewee_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewer_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reviewer_id", "reviewee_id", name="uq_review_pair"),
    )
    op.create_index(op.f("ix_reviews_id"), "reviews", ["id"], unique=False)
    op.create_index(op.f("ix_reviews_reviewee_id"), "reviews", ["reviewee_id"], unique=False)
    op.create_index(op.f("ix_reviews_reviewer_id"), "reviews", ["reviewer_id"], unique=False)

    op.create_table(
        "learning_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("creator_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("city", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("availability", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["creator_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_learning_requests_creator_id"), "learning_requests", ["creator_id"], unique=False)
    op.create_index(op.f("ix_learning_requests_id"), "learning_requests", ["id"], unique=False)
    op.create_index(op.f("ix_learning_requests_skill_id"), "learning_requests", ["skill_id"], unique=False)
    op.create_index(op.f("ix_learning_requests_status"), "learning_requests", ["status"], unique=False)

    op.create_table(
        "learning_request_applications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("request_id", sa.Integer(), nullable=False),
        sa.Column("applicant_id", sa.Integer(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["applicant_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["request_id"], ["learning_requests.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("request_id", "applicant_id", name="uq_request_applicant"),
    )
    op.create_index(op.f("ix_learning_request_applications_applicant_id"), "learning_request_applications", ["applicant_id"], unique=False)
    op.create_index(op.f("ix_learning_request_applications_id"), "learning_request_applications", ["id"], unique=False)
    op.create_index(op.f("ix_learning_request_applications_request_id"), "learning_request_applications", ["request_id"], unique=False)
    op.create_index(op.f("ix_learning_request_applications_status"), "learning_request_applications", ["status"], unique=False)

    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_password_reset_tokens_id"), "password_reset_tokens", ["id"], unique=False)
    op.create_index(op.f("ix_password_reset_tokens_token_hash"), "password_reset_tokens", ["token_hash"], unique=True)
    op.create_index(op.f("ix_password_reset_tokens_user_id"), "password_reset_tokens", ["user_id"], unique=False)

    op.create_table(
        "email_verification_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_email_verification_tokens_id"), "email_verification_tokens", ["id"], unique=False)
    op.create_index(op.f("ix_email_verification_tokens_token_hash"), "email_verification_tokens", ["token_hash"], unique=True)
    op.create_index(op.f("ix_email_verification_tokens_user_id"), "email_verification_tokens", ["user_id"], unique=False)

    op.create_table(
        "oauth_accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("provider_user_id", sa.String(length=255), nullable=False),
        sa.Column("provider_email", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "provider_user_id", name="uq_oauth_provider_user"),
    )
    op.create_index(op.f("ix_oauth_accounts_id"), "oauth_accounts", ["id"], unique=False)
    op.create_index(op.f("ix_oauth_accounts_provider"), "oauth_accounts", ["provider"], unique=False)
    op.create_index(op.f("ix_oauth_accounts_user_id"), "oauth_accounts", ["user_id"], unique=False)

    op.add_column("messages", sa.Column("message_type", sa.String(length=20), nullable=False, server_default="text"))
    op.add_column("messages", sa.Column("attachment_filename", sa.String(length=255), nullable=True))
    op.add_column("messages", sa.Column("attachment_content_type", sa.String(length=120), nullable=True))
    op.add_column("messages", sa.Column("attachment_data", sa.LargeBinary(), nullable=True))
    op.add_column("messages", sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("messages", "delivered_at")
    op.drop_column("messages", "attachment_data")
    op.drop_column("messages", "attachment_content_type")
    op.drop_column("messages", "attachment_filename")
    op.drop_column("messages", "message_type")

    op.drop_index(op.f("ix_oauth_accounts_user_id"), table_name="oauth_accounts")
    op.drop_index(op.f("ix_oauth_accounts_provider"), table_name="oauth_accounts")
    op.drop_index(op.f("ix_oauth_accounts_id"), table_name="oauth_accounts")
    op.drop_table("oauth_accounts")

    op.drop_index(op.f("ix_email_verification_tokens_user_id"), table_name="email_verification_tokens")
    op.drop_index(op.f("ix_email_verification_tokens_token_hash"), table_name="email_verification_tokens")
    op.drop_index(op.f("ix_email_verification_tokens_id"), table_name="email_verification_tokens")
    op.drop_table("email_verification_tokens")

    op.drop_index(op.f("ix_password_reset_tokens_user_id"), table_name="password_reset_tokens")
    op.drop_index(op.f("ix_password_reset_tokens_token_hash"), table_name="password_reset_tokens")
    op.drop_index(op.f("ix_password_reset_tokens_id"), table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")

    op.drop_index(op.f("ix_learning_request_applications_status"), table_name="learning_request_applications")
    op.drop_index(op.f("ix_learning_request_applications_request_id"), table_name="learning_request_applications")
    op.drop_index(op.f("ix_learning_request_applications_id"), table_name="learning_request_applications")
    op.drop_index(op.f("ix_learning_request_applications_applicant_id"), table_name="learning_request_applications")
    op.drop_table("learning_request_applications")

    op.drop_index(op.f("ix_learning_requests_status"), table_name="learning_requests")
    op.drop_index(op.f("ix_learning_requests_skill_id"), table_name="learning_requests")
    op.drop_index(op.f("ix_learning_requests_id"), table_name="learning_requests")
    op.drop_index(op.f("ix_learning_requests_creator_id"), table_name="learning_requests")
    op.drop_table("learning_requests")

    op.drop_index(op.f("ix_reviews_reviewer_id"), table_name="reviews")
    op.drop_index(op.f("ix_reviews_reviewee_id"), table_name="reviews")
    op.drop_index(op.f("ix_reviews_id"), table_name="reviews")
    op.drop_table("reviews")

    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_type"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_id"), table_name="notifications")
    op.drop_table("notifications")

    op.drop_index(op.f("ix_follows_id"), table_name="follows")
    op.drop_index(op.f("ix_follows_follower_id"), table_name="follows")
    op.drop_index(op.f("ix_follows_followed_id"), table_name="follows")
    op.drop_table("follows")

    op.drop_index(op.f("ix_user_wanted_skills_user_id"), table_name="user_wanted_skills")
    op.drop_index(op.f("ix_user_wanted_skills_skill_id"), table_name="user_wanted_skills")
    op.drop_index(op.f("ix_user_wanted_skills_id"), table_name="user_wanted_skills")
    op.drop_table("user_wanted_skills")

    op.drop_index(op.f("ix_user_offered_skills_user_id"), table_name="user_offered_skills")
    op.drop_index(op.f("ix_user_offered_skills_skill_id"), table_name="user_offered_skills")
    op.drop_index(op.f("ix_user_offered_skills_id"), table_name="user_offered_skills")
    op.drop_table("user_offered_skills")

    op.drop_index(op.f("ix_skills_slug"), table_name="skills")
    op.drop_index(op.f("ix_skills_name"), table_name="skills")
    op.drop_index(op.f("ix_skills_id"), table_name="skills")
    op.drop_table("skills")

    op.drop_index(op.f("ix_user_profiles_user_id"), table_name="user_profiles")
    op.drop_index(op.f("ix_user_profiles_id"), table_name="user_profiles")
    op.drop_table("user_profiles")

    op.drop_column("users", "last_active_at")
    op.drop_column("users", "is_admin")
    op.drop_column("users", "is_verified")

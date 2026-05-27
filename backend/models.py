from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
    )

    profile: Mapped["UserProfile"] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    offered_skills: Mapped[list["UserOfferedSkill"]] = relationship(
        "UserOfferedSkill",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    wanted_skills: Mapped[list["UserWantedSkill"]] = relationship(
        "UserWantedSkill",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sent_friend_requests: Mapped[list["FriendRequest"]] = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan",
    )
    received_friend_requests: Mapped[list["FriendRequest"]] = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.receiver_id",
        back_populates="receiver",
        cascade="all, delete-orphan",
    )
    sent_messages: Mapped[list["Message"]] = relationship(
        "Message",
        foreign_keys="Message.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan",
    )
    received_messages: Mapped[list["Message"]] = relationship(
        "Message",
        foreign_keys="Message.receiver_id",
        back_populates="receiver",
        cascade="all, delete-orphan",
    )
    sent_reviews: Mapped[list["Review"]] = relationship(
        "Review",
        foreign_keys="Review.reviewer_id",
        back_populates="reviewer",
        cascade="all, delete-orphan",
    )
    received_reviews: Mapped[list["Review"]] = relationship(
        "Review",
        foreign_keys="Review.reviewee_id",
        back_populates="reviewee",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    followers: Mapped[list["Follow"]] = relationship(
        "Follow",
        foreign_keys="Follow.followed_id",
        back_populates="followed",
        cascade="all, delete-orphan",
    )
    following: Mapped[list["Follow"]] = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",
    )
    learning_requests: Mapped[list["LearningRequest"]] = relationship(
        "LearningRequest",
        back_populates="creator",
        cascade="all, delete-orphan",
    )
    learning_applications: Mapped[list["LearningRequestApplication"]] = relationship(
        "LearningRequestApplication",
        back_populates="applicant",
        cascade="all, delete-orphan",
    )
    password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    email_verification_tokens: Mapped[list["EmailVerificationToken"]] = relationship(
        "EmailVerificationToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(
        "OAuthAccount",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    bio: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    city: Mapped[str] = mapped_column(String(120), nullable=False, default="", server_default="")
    availability: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    experience_level: Mapped[str] = mapped_column(String(40), nullable=False, default="intermediate", server_default="intermediate")
    avatar_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_content_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    avatar_data: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    avatar_storage_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_public_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    linkedin_url: Mapped[str] = mapped_column(String(255), nullable=False, default="", server_default="")
    website_url: Mapped[str] = mapped_column(String(255), nullable=False, default="", server_default="")
    x_url: Mapped[str] = mapped_column(String(255), nullable=False, default="", server_default="")
    rating_average: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0")
    rating_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    user: Mapped["User"] = relationship("User", back_populates="profile")


class Skill(Base):
    __tablename__ = "skills"
    __table_args__ = (UniqueConstraint("slug", name="uq_skills_slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(140), nullable=False, unique=True, index=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False, default="general", server_default="general")

    offered_by_users: Mapped[list["UserOfferedSkill"]] = relationship(
        "UserOfferedSkill",
        back_populates="skill",
        cascade="all, delete-orphan",
    )
    wanted_by_users: Mapped[list["UserWantedSkill"]] = relationship(
        "UserWantedSkill",
        back_populates="skill",
        cascade="all, delete-orphan",
    )
    marketplace_requests: Mapped[list["LearningRequest"]] = relationship(
        "LearningRequest",
        back_populates="skill",
    )


class UserOfferedSkill(Base):
    __tablename__ = "user_offered_skills"
    __table_args__ = (UniqueConstraint("user_id", "skill_id", name="uq_user_offered_skill"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), index=True)

    user: Mapped["User"] = relationship("User", back_populates="offered_skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="offered_by_users")


class UserWantedSkill(Base):
    __tablename__ = "user_wanted_skills"
    __table_args__ = (UniqueConstraint("user_id", "skill_id", name="uq_user_wanted_skill"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), index=True)

    user: Mapped["User"] = relationship("User", back_populates="wanted_skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="wanted_by_users")


class FriendRequest(Base):
    __tablename__ = "friend_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
    )

    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_id], back_populates="sent_friend_requests")
    receiver: Mapped["User"] = relationship("User", foreign_keys=[receiver_id], back_populates="received_friend_requests")


class Follow(Base):
    __tablename__ = "follows"
    __table_args__ = (UniqueConstraint("follower_id", "followed_id", name="uq_follow_pair"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    followed_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
    )

    follower: Mapped["User"] = relationship("User", foreign_keys=[follower_id], back_populates="following")
    followed: Mapped["User"] = relationship("User", foreign_keys=[followed_id], back_populates="followers")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    link_url: Mapped[str] = mapped_column(String(255), nullable=False, default="", server_default="")
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship("User", back_populates="notifications")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    message_type: Mapped[str] = mapped_column(String(20), nullable=False, default="text", server_default="text")
    attachment_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    attachment_content_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    attachment_data: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    attachment_storage_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    attachment_public_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
    )
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver: Mapped["User"] = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("reviewer_id", "reviewee_id", name="uq_review_pair"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    reviewee_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    endorsement: Mapped[str] = mapped_column(String(160), nullable=False, default="", server_default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
    )

    reviewer: Mapped["User"] = relationship("User", foreign_keys=[reviewer_id], back_populates="sent_reviews")
    reviewee: Mapped["User"] = relationship("User", foreign_keys=[reviewee_id], back_populates="received_reviews")


class LearningRequest(Base, TimestampMixin):
    __tablename__ = "learning_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="RESTRICT"), index=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False, default="", server_default="")
    availability: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open", server_default="open", index=True)

    creator: Mapped["User"] = relationship("User", back_populates="learning_requests")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="marketplace_requests")
    applications: Mapped[list["LearningRequestApplication"]] = relationship(
        "LearningRequestApplication",
        back_populates="request",
        cascade="all, delete-orphan",
    )


class LearningRequestApplication(Base, TimestampMixin):
    __tablename__ = "learning_request_applications"
    __table_args__ = (UniqueConstraint("request_id", "applicant_id", name="uq_request_applicant"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("learning_requests.id", ondelete="CASCADE"), index=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", server_default="pending", index=True)

    request: Mapped["LearningRequest"] = relationship("LearningRequest", back_populates="applications")
    applicant: Mapped["User"] = relationship("User", back_populates="learning_applications")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship("User", back_populates="password_reset_tokens")


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship("User", back_populates="email_verification_tokens")


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"
    __table_args__ = (UniqueConstraint("provider", "provider_user_id", name="uq_oauth_provider_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_email: Mapped[str] = mapped_column(String(255), nullable=False, default="", server_default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship("User", back_populates="oauth_accounts")

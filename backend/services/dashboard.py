from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas
from .matchmaking import get_top_matches
from .notifications import list_notifications


def build_dashboard_summary(db: Session, current_user: models.User) -> schemas.DashboardSummaryResponse:
    accepted_connections = db.execute(
        select(func.count(models.FriendRequest.id)).where(
            models.FriendRequest.status == "accepted",
            or_(
                models.FriendRequest.sender_id == current_user.id,
                models.FriendRequest.receiver_id == current_user.id,
            ),
        )
    ).scalar_one()
    pending_requests = db.execute(
        select(func.count(models.FriendRequest.id)).where(
            models.FriendRequest.receiver_id == current_user.id,
            models.FriendRequest.status == "pending",
        )
    ).scalar_one()
    messages_sent = db.execute(
        select(func.count(models.Message.id)).where(models.Message.sender_id == current_user.id)
    ).scalar_one()
    messages_received = db.execute(
        select(func.count(models.Message.id)).where(models.Message.receiver_id == current_user.id)
    ).scalar_one()
    unread_messages = db.execute(
        select(func.count(models.Message.id)).where(
            models.Message.receiver_id == current_user.id,
            models.Message.read_at.is_(None),
        )
    ).scalar_one()
    reviews_count = current_user.profile.rating_count if current_user.profile else 0

    notifications = [schemas.NotificationResponse.model_validate(item) for item in list_notifications(db, user_id=current_user.id, limit=5)]
    recent_messages = list(
        db.execute(
            select(models.Message)
            .where(
                or_(
                    models.Message.sender_id == current_user.id,
                    models.Message.receiver_id == current_user.id,
                )
            )
            .order_by(models.Message.created_at.desc())
            .limit(3)
        ).scalars()
    )

    activity = [
        schemas.DashboardActivityItem(
            title=(
                f"Conversation with user #{message.receiver_id if message.sender_id == current_user.id else message.sender_id}"
            ),
            body=(message.content or "Sent an attachment.")[:160],
            time=message.created_at.astimezone(timezone.utc).strftime("%b %d, %H:%M UTC"),
        )
        for message in recent_messages
    ]

    if not activity:
        activity = [
            schemas.DashboardActivityItem(
                title="Complete your profile",
                body="Add skills offered and wanted so the system can generate stronger matches.",
                time="Just now",
            )
        ]

    if current_user.offered_skills and current_user.wanted_skills:
        suggested_matches = get_top_matches(
            db,
            skill_offer=current_user.offered_skills[0].skill.name,
            skill_want=current_user.wanted_skills[0].skill.name,
            current_user_id=current_user.id,
            limit=3,
        )
    else:
        suggested_matches = []

    skills = [
        schemas.DashboardSkillItem(
            label=item.skill.name,
            value=min(100, 40 + (index * 15) + reviews_count * 5),
            note="Profile visibility improves when this skill is clearly positioned.",
        )
        for index, item in enumerate(current_user.offered_skills[:3])
    ]

    if not skills:
        skills = [
            schemas.DashboardSkillItem(
                label="Add your first skill",
                value=35,
                note="Once you add skills, matchmaking and discovery become meaningful.",
            )
        ]

    upcoming = [
        schemas.DashboardSessionItem(
            title=f"{application.request.skill.name} request application",
            time=application.created_at.astimezone(timezone.utc).strftime("%b %d, %H:%M UTC"),
        )
        for application in current_user.learning_applications[:3]
    ]

    if not upcoming:
        upcoming = [
            schemas.DashboardSessionItem(
                title="No active exchanges yet",
                time="Create or apply to a marketplace request to start.",
            )
        ]

    reply_rate = "100%" if messages_sent and not unread_messages else f"{max(0, 100 - (unread_messages * 10))}%"

    return schemas.DashboardSummaryResponse(
        stats=[
            schemas.DashboardStat(label="Active matches", value=str(accepted_connections), delta=f"{pending_requests} pending requests"),
            schemas.DashboardStat(label="Reply rate", value=reply_rate, delta=f"{messages_received} messages received"),
            schemas.DashboardStat(label="Marketplace activity", value=str(len(current_user.learning_requests)), delta=f"{len(current_user.learning_applications)} applications made"),
            schemas.DashboardStat(label="Trust score", value=f"{round(current_user.profile.rating_average, 1) if current_user.profile else 0}/5", delta=f"{reviews_count} reviews"),
        ],
        activity=activity,
        suggested_matches=[schemas.MatchResult(**item) for item in suggested_matches],
        upcoming=upcoming,
        skills=skills,
        notifications=notifications,
        pending_requests=pending_requests,
        unread_messages=unread_messages,
    )

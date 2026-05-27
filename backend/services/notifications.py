from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models


def create_notification(
    db: Session,
    *,
    user_id: int,
    notification_type: str,
    title: str,
    body: str,
    link_url: str = "",
) -> models.Notification:
    notification = models.Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        body=body,
        link_url=link_url,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def list_notifications(db: Session, *, user_id: int, limit: int = 20) -> list[models.Notification]:
    return list(
        db.execute(
            select(models.Notification)
            .where(models.Notification.user_id == user_id)
            .order_by(models.Notification.created_at.desc(), models.Notification.id.desc())
            .limit(limit)
        ).scalars()
    )


def mark_notification_read(
    db: Session,
    *,
    notification_id: int,
    user_id: int,
) -> models.Notification | None:
    notification = db.execute(
        select(models.Notification).where(
            models.Notification.id == notification_id,
            models.Notification.user_id == user_id,
        )
    ).scalar_one_or_none()
    if not notification:
        return None
    notification.is_read = True
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

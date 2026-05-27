from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.orm import Session, joinedload

from .. import models
from .notifications import create_notification
from .storage import upload_file
from .users import get_avatar_url

PENDING = "pending"
ACCEPTED = "accepted"
REJECTED = "rejected"
VALID_REQUEST_STATUSES = {PENDING, ACCEPTED, REJECTED}


def get_user_or_none(db: Session, user_id: int) -> models.User | None:
    return db.execute(
        select(models.User)
        .options(joinedload(models.User.profile), joinedload(models.User.followers), joinedload(models.User.following))
        .where(models.User.id == user_id)
    ).unique().scalar_one_or_none()


def get_friend_request_or_none(db: Session, request_id: int) -> models.FriendRequest | None:
    return db.execute(
        select(models.FriendRequest)
        .options(
            joinedload(models.FriendRequest.sender).joinedload(models.User.profile),
            joinedload(models.FriendRequest.receiver).joinedload(models.User.profile),
        )
        .where(models.FriendRequest.id == request_id)
    ).unique().scalar_one_or_none()


def get_friendship_request_between(db: Session, user_a_id: int, user_b_id: int) -> models.FriendRequest | None:
    return db.execute(
        select(models.FriendRequest)
        .options(joinedload(models.FriendRequest.sender), joinedload(models.FriendRequest.receiver))
        .where(
            or_(
                and_(models.FriendRequest.sender_id == user_a_id, models.FriendRequest.receiver_id == user_b_id),
                and_(models.FriendRequest.sender_id == user_b_id, models.FriendRequest.receiver_id == user_a_id),
            )
        )
        .order_by(models.FriendRequest.created_at.desc())
    ).scalars().first()


def are_friends(db: Session, user_a_id: int, user_b_id: int) -> bool:
    request = get_friendship_request_between(db, user_a_id, user_b_id)
    return bool(request and request.status == ACCEPTED)


def create_friend_request(db: Session, sender: models.User, receiver: models.User) -> models.FriendRequest:
    friend_request = models.FriendRequest(sender_id=sender.id, receiver_id=receiver.id, status=PENDING)
    db.add(friend_request)
    db.commit()
    db.refresh(friend_request)
    create_notification(
        db,
        user_id=receiver.id,
        notification_type="friend_request",
        title=f"{sender.name} sent a connection request",
        body=f"{sender.name} wants to exchange skills with you.",
        link_url="/chat",
    )
    return get_friend_request_or_none(db, friend_request.id) or friend_request


def update_friend_request_status(
    db: Session,
    friend_request: models.FriendRequest,
    *,
    status: str,
) -> models.FriendRequest:
    if status not in VALID_REQUEST_STATUSES:
        raise ValueError("Unsupported friend request status.")

    friend_request.status = status
    friend_request.updated_at = datetime.now(timezone.utc)
    db.add(friend_request)
    db.commit()
    db.refresh(friend_request)

    if status == ACCEPTED:
        create_notification(
            db,
            user_id=friend_request.sender_id,
            notification_type="friend_request_accepted",
            title=f"{friend_request.receiver.name} accepted your request",
            body="You can now start a realtime chat.",
            link_url="/chat",
        )
    elif status == REJECTED:
        create_notification(
            db,
            user_id=friend_request.sender_id,
            notification_type="friend_request_rejected",
            title=f"{friend_request.receiver.name} declined your request",
            body="The connection request was declined.",
            link_url="/matches",
        )

    return get_friend_request_or_none(db, friend_request.id) or friend_request


def create_message(
    db: Session,
    sender: models.User,
    receiver: models.User,
    content: str,
    *,
    message_type: str = "text",
    attachment_filename: str | None = None,
    attachment_content_type: str | None = None,
    attachment_data: bytes | None = None,
) -> models.Message:
    stored_asset = None
    if attachment_data and attachment_filename:
        stored_asset = upload_file(
            data=attachment_data,
            content_type=attachment_content_type or "application/octet-stream",
            folder="chat",
            filename=attachment_filename,
        )

    message = models.Message(
        sender_id=sender.id,
        receiver_id=receiver.id,
        content=content.strip(),
        message_type=message_type,
        attachment_filename=attachment_filename,
        attachment_content_type=attachment_content_type,
        attachment_data=None if stored_asset else attachment_data,
        attachment_storage_path=stored_asset.storage_path if stored_asset else None,
        attachment_public_url=stored_asset.public_url if stored_asset else None,
        delivered_at=datetime.now(timezone.utc),
    )
    db.add(message)
    sender.last_active_at = datetime.now(timezone.utc)
    receiver.last_active_at = datetime.now(timezone.utc)
    db.add(sender)
    db.add(receiver)
    db.commit()
    db.refresh(message)

    create_notification(
        db,
        user_id=receiver.id,
        notification_type="message",
        title=f"New message from {sender.name}",
        body=content[:160] if content else "Sent an attachment.",
        link_url="/chat",
    )
    return message


def get_attachment_url(message: models.Message) -> str | None:
    if message.attachment_public_url:
        return message.attachment_public_url
    if message.attachment_data:
        return f"/messages/attachments/{message.id}"
    return None


def get_messages_between_users(db: Session, user_a_id: int, user_b_id: int) -> list[models.Message]:
    return list(
        db.execute(
            select(models.Message)
            .where(
                or_(
                    and_(models.Message.sender_id == user_a_id, models.Message.receiver_id == user_b_id),
                    and_(models.Message.sender_id == user_b_id, models.Message.receiver_id == user_a_id),
                )
            )
            .order_by(models.Message.created_at.asc(), models.Message.id.asc())
        ).scalars()
    )


def mark_messages_as_read(db: Session, *, reader_id: int, other_user_id: int) -> list[int]:
    messages = list(
        db.execute(
            select(models.Message).where(
                models.Message.sender_id == other_user_id,
                models.Message.receiver_id == reader_id,
                models.Message.read_at.is_(None),
            )
        ).scalars()
    )

    if not messages:
        return []

    now = datetime.now(timezone.utc)
    ids: list[int] = []
    for message in messages:
        message.read_at = now
        ids.append(message.id)
        db.add(message)

    db.commit()
    return ids


def build_friend_overview(db: Session, current_user: models.User, *, online_user_ids: set[int] | None = None) -> dict:
    online_user_ids = online_user_ids or set()
    accepted_requests = list(
        db.execute(
            select(models.FriendRequest)
            .options(
                joinedload(models.FriendRequest.sender).joinedload(models.User.profile),
                joinedload(models.FriendRequest.receiver).joinedload(models.User.profile),
            )
            .where(
                models.FriendRequest.status == ACCEPTED,
                or_(
                    models.FriendRequest.sender_id == current_user.id,
                    models.FriendRequest.receiver_id == current_user.id,
                ),
            )
            .order_by(models.FriendRequest.updated_at.desc(), models.FriendRequest.created_at.desc())
        ).unique().scalars()
    )

    incoming_requests = list(
        db.execute(
            select(models.FriendRequest)
            .options(
                joinedload(models.FriendRequest.sender).joinedload(models.User.profile),
                joinedload(models.FriendRequest.receiver).joinedload(models.User.profile),
            )
            .where(models.FriendRequest.receiver_id == current_user.id, models.FriendRequest.status == PENDING)
            .order_by(models.FriendRequest.created_at.desc())
        ).unique().scalars()
    )

    outgoing_requests = list(
        db.execute(
            select(models.FriendRequest)
            .options(
                joinedload(models.FriendRequest.sender).joinedload(models.User.profile),
                joinedload(models.FriendRequest.receiver).joinedload(models.User.profile),
            )
            .where(models.FriendRequest.sender_id == current_user.id, models.FriendRequest.status == PENDING)
            .order_by(models.FriendRequest.created_at.desc())
        ).unique().scalars()
    )

    followers = list(
        db.execute(
            select(models.Follow)
            .options(joinedload(models.Follow.follower).joinedload(models.User.profile))
            .where(models.Follow.followed_id == current_user.id)
            .order_by(models.Follow.created_at.desc())
        ).scalars()
    )
    following = list(
        db.execute(
            select(models.Follow)
            .options(joinedload(models.Follow.followed).joinedload(models.User.profile))
            .where(models.Follow.follower_id == current_user.id)
            .order_by(models.Follow.created_at.desc())
        ).scalars()
    )

    friends: list[dict] = []
    for request in accepted_requests:
        friend = request.receiver if request.sender_id == current_user.id else request.sender
        latest_message = db.execute(
            select(models.Message)
            .where(
                or_(
                    and_(models.Message.sender_id == current_user.id, models.Message.receiver_id == friend.id),
                    and_(models.Message.sender_id == friend.id, models.Message.receiver_id == current_user.id),
                )
            )
            .order_by(models.Message.created_at.desc(), models.Message.id.desc())
            .limit(1)
        ).scalar_one_or_none()

        friends.append(
            {
                "id": friend.id,
                "name": friend.name,
                "email": friend.email,
                "avatar_url": get_avatar_url(friend),
                "city": friend.profile.city if friend.profile else "",
                "rating_average": round(friend.profile.rating_average, 2) if friend.profile else 0,
                "latest_message_preview": latest_message.content if latest_message else None,
                "last_message_at": latest_message.created_at if latest_message else None,
                "is_online": friend.id in online_user_ids,
            }
        )

    friends.sort(
        key=lambda item: (
            item["last_message_at"] is not None,
            item["last_message_at"] or datetime.min.replace(tzinfo=timezone.utc),
        ),
        reverse=True,
    )

    return {
        "friends": friends,
        "incoming_requests": incoming_requests,
        "outgoing_requests": outgoing_requests,
        "followers": [follow.follower for follow in followers],
        "following": [follow.followed for follow in following],
    }


def follow_user(db: Session, *, follower: models.User, followed: models.User) -> models.Follow:
    existing = db.execute(
        select(models.Follow).where(
            models.Follow.follower_id == follower.id,
            models.Follow.followed_id == followed.id,
        )
    ).scalar_one_or_none()
    if existing:
        return existing

    follow = models.Follow(follower_id=follower.id, followed_id=followed.id)
    db.add(follow)
    db.commit()
    db.refresh(follow)
    create_notification(
        db,
        user_id=followed.id,
        notification_type="follow",
        title=f"{follower.name} followed you",
        body="They can now keep up with your activity and profile updates.",
        link_url="/profile",
    )
    return follow


def unfollow_user(db: Session, *, follower_id: int, followed_id: int) -> bool:
    follow = db.execute(
        select(models.Follow).where(
            models.Follow.follower_id == follower_id,
            models.Follow.followed_id == followed_id,
        )
    ).scalar_one_or_none()
    if not follow:
        return False

    db.delete(follow)
    db.commit()
    return True


def create_review(
    db: Session,
    *,
    reviewer: models.User,
    reviewee: models.User,
    rating: int,
    comment: str,
    endorsement: str,
) -> models.Review:
    existing = db.execute(
        select(models.Review).where(
            models.Review.reviewer_id == reviewer.id,
            models.Review.reviewee_id == reviewee.id,
        )
    ).scalar_one_or_none()

    if existing:
        existing.rating = rating
        existing.comment = comment.strip()
        existing.endorsement = endorsement.strip()
        db.add(existing)
        review = existing
    else:
        review = models.Review(
            reviewer_id=reviewer.id,
            reviewee_id=reviewee.id,
            rating=rating,
            comment=comment.strip(),
            endorsement=endorsement.strip(),
        )
        db.add(review)

    db.commit()
    db.refresh(review)
    recalculate_rating(db, reviewee.id)
    create_notification(
        db,
        user_id=reviewee.id,
        notification_type="review",
        title=f"{reviewer.name} left you a review",
        body=f"{rating}/5 rating with endorsement: {endorsement.strip() or 'New endorsement'}",
        link_url="/profile",
    )
    return review


def recalculate_rating(db: Session, user_id: int) -> None:
    profile = db.execute(select(models.UserProfile).where(models.UserProfile.user_id == user_id)).scalar_one_or_none()
    if not profile:
        return

    ratings = list(
        db.execute(select(models.Review.rating).where(models.Review.reviewee_id == user_id)).scalars()
    )
    profile.rating_count = len(ratings)
    profile.rating_average = round(sum(ratings) / len(ratings), 2) if ratings else 0
    db.add(profile)
    db.commit()

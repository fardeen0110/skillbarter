from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, joinedload

from ..models import FriendRequest, Message, User

PENDING = "pending"
ACCEPTED = "accepted"
REJECTED = "rejected"
VALID_REQUEST_STATUSES = {PENDING, ACCEPTED, REJECTED}


def get_user_or_none(db: Session, user_id: int) -> User | None:
    return db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()


def get_friend_request_or_none(db: Session, request_id: int) -> FriendRequest | None:
    statement = (
        select(FriendRequest)
        .options(joinedload(FriendRequest.sender), joinedload(FriendRequest.receiver))
        .where(FriendRequest.id == request_id)
    )
    return db.execute(statement).scalar_one_or_none()


def get_friendship_request_between(db: Session, user_a_id: int, user_b_id: int) -> FriendRequest | None:
    statement = (
        select(FriendRequest)
        .options(joinedload(FriendRequest.sender), joinedload(FriendRequest.receiver))
        .where(
            or_(
                and_(
                    FriendRequest.sender_id == user_a_id,
                    FriendRequest.receiver_id == user_b_id,
                ),
                and_(
                    FriendRequest.sender_id == user_b_id,
                    FriendRequest.receiver_id == user_a_id,
                ),
            )
        )
        .order_by(FriendRequest.created_at.desc())
    )
    return db.execute(statement).scalars().first()


def are_friends(db: Session, user_a_id: int, user_b_id: int) -> bool:
    request = get_friendship_request_between(db, user_a_id, user_b_id)
    return bool(request and request.status == ACCEPTED)


def create_friend_request(db: Session, sender: User, receiver: User) -> FriendRequest:
    friend_request = FriendRequest(
        sender_id=sender.id,
        receiver_id=receiver.id,
        status=PENDING,
    )
    db.add(friend_request)
    db.commit()
    db.refresh(friend_request)
    return get_friend_request_or_none(db, friend_request.id) or friend_request


def update_friend_request_status(
    db: Session,
    friend_request: FriendRequest,
    *,
    status: str,
) -> FriendRequest:
    if status not in VALID_REQUEST_STATUSES:
        raise ValueError("Unsupported friend request status.")

    friend_request.status = status
    friend_request.updated_at = datetime.now(timezone.utc)
    db.add(friend_request)
    db.commit()
    db.refresh(friend_request)
    return get_friend_request_or_none(db, friend_request.id) or friend_request


def create_message(db: Session, sender: User, receiver: User, content: str) -> Message:
    message = Message(
        sender_id=sender.id,
        receiver_id=receiver.id,
        content=content.strip(),
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_messages_between_users(db: Session, user_a_id: int, user_b_id: int) -> list[Message]:
    statement = (
        select(Message)
        .where(
            or_(
                and_(Message.sender_id == user_a_id, Message.receiver_id == user_b_id),
                and_(Message.sender_id == user_b_id, Message.receiver_id == user_a_id),
            )
        )
        .order_by(Message.created_at.asc(), Message.id.asc())
    )
    return list(db.execute(statement).scalars().all())


def mark_messages_as_read(db: Session, *, reader_id: int, other_user_id: int) -> None:
    messages = db.execute(
        select(Message).where(
            Message.sender_id == other_user_id,
            Message.receiver_id == reader_id,
            Message.read_at.is_(None),
        )
    ).scalars()

    now = datetime.now(timezone.utc)
    updated = False
    for message in messages:
        message.read_at = now
        db.add(message)
        updated = True

    if updated:
        db.commit()


def build_friend_overview(db: Session, current_user: User) -> dict:
    accepted_requests = list(
        db.execute(
            select(FriendRequest)
            .options(joinedload(FriendRequest.sender), joinedload(FriendRequest.receiver))
            .where(
                FriendRequest.status == ACCEPTED,
                or_(
                    FriendRequest.sender_id == current_user.id,
                    FriendRequest.receiver_id == current_user.id,
                ),
            )
            .order_by(FriendRequest.updated_at.desc(), FriendRequest.created_at.desc())
        ).scalars()
    )

    incoming_requests = list(
        db.execute(
            select(FriendRequest)
            .options(joinedload(FriendRequest.sender), joinedload(FriendRequest.receiver))
            .where(
                FriendRequest.receiver_id == current_user.id,
                FriendRequest.status == PENDING,
            )
            .order_by(FriendRequest.created_at.desc())
        ).scalars()
    )

    outgoing_requests = list(
        db.execute(
            select(FriendRequest)
            .options(joinedload(FriendRequest.sender), joinedload(FriendRequest.receiver))
            .where(
                FriendRequest.sender_id == current_user.id,
                FriendRequest.status == PENDING,
            )
            .order_by(FriendRequest.created_at.desc())
        ).scalars()
    )

    friends: list[dict] = []
    for request in accepted_requests:
        friend = request.receiver if request.sender_id == current_user.id else request.sender
        latest_message = db.execute(
            select(Message)
            .where(
                or_(
                    and_(Message.sender_id == current_user.id, Message.receiver_id == friend.id),
                    and_(Message.sender_id == friend.id, Message.receiver_id == current_user.id),
                )
            )
            .order_by(Message.created_at.desc(), Message.id.desc())
            .limit(1)
        ).scalar_one_or_none()

        friends.append(
            {
                "id": friend.id,
                "name": friend.name,
                "email": friend.email,
                "latest_message_preview": latest_message.content if latest_message else None,
                "last_message_at": latest_message.created_at if latest_message else None,
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
    }

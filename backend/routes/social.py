from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db
from ..services.realtime import realtime_manager
from ..services.social import (
    ACCEPTED,
    PENDING,
    REJECTED,
    are_friends,
    build_friend_overview,
    create_friend_request,
    create_message,
    create_review,
    follow_user,
    get_attachment_url,
    get_friend_request_or_none,
    get_friendship_request_between,
    get_messages_between_users,
    get_user_or_none,
    mark_messages_as_read,
    unfollow_user,
    update_friend_request_status,
)
from ..services.users import serialize_user_mini

router = APIRouter(tags=["Social"])


def serialize_friend_request(friend_request) -> schemas.FriendRequestResponse:
    return schemas.FriendRequestResponse(
        id=friend_request.id,
        sender=serialize_user_mini(friend_request.sender),
        receiver=serialize_user_mini(friend_request.receiver),
        status=friend_request.status,
        created_at=friend_request.created_at,
        updated_at=friend_request.updated_at,
    )


def serialize_message(message: models.Message, current_user_id: int) -> schemas.MessageResponse:
    return schemas.MessageResponse(
        id=message.id,
        sender_id=message.sender_id,
        receiver_id=message.receiver_id,
        content=message.content,
        created_at=message.created_at,
        delivered_at=message.delivered_at,
        read_at=message.read_at,
        is_mine=message.sender_id == current_user_id,
        message_type=message.message_type,
        attachment_url=get_attachment_url(message),
        attachment_filename=message.attachment_filename,
    )


@router.post("/send-request", response_model=schemas.FriendRequestResponse, status_code=status.HTTP_201_CREATED)
async def send_request(
    payload: schemas.FriendRequestCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.receiver_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot send a request to yourself.")

    receiver = get_user_or_none(db, payload.receiver_id)
    if not receiver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found.")

    existing_request = get_friendship_request_between(db, current_user.id, receiver.id)
    if existing_request:
        if existing_request.status == ACCEPTED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are already connected.")
        if existing_request.status == PENDING:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A pending request already exists.")
        if existing_request.status == REJECTED and existing_request.sender_id == current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="That request was already rejected.")

    friend_request = create_friend_request(db, current_user, receiver)

    await realtime_manager.send_to_user(
        receiver.id,
        {
            "type": "request:new",
            "request": serialize_friend_request(friend_request).model_dump(mode="json"),
            "message": f"{current_user.name} sent you a match request.",
        },
    )
    return serialize_friend_request(friend_request)


@router.post("/accept-request", response_model=schemas.FriendRequestResponse)
async def accept_request(
    payload: schemas.FriendRequestAction,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    friend_request = get_friend_request_or_none(db, payload.request_id)
    if not friend_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found.")
    if friend_request.receiver_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot accept this request.")
    if friend_request.status != PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This request is no longer pending.")

    friend_request = update_friend_request_status(db, friend_request, status=ACCEPTED)

    await realtime_manager.send_to_user(
        friend_request.sender_id,
        {
            "type": "request:accepted",
            "request": serialize_friend_request(friend_request).model_dump(mode="json"),
            "message": f"{current_user.name} accepted your match request.",
        },
    )
    return serialize_friend_request(friend_request)


@router.post("/reject-request", response_model=schemas.FriendRequestResponse)
async def reject_request(
    payload: schemas.FriendRequestAction,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    friend_request = get_friend_request_or_none(db, payload.request_id)
    if not friend_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found.")
    if friend_request.receiver_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot reject this request.")
    if friend_request.status != PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This request is no longer pending.")

    friend_request = update_friend_request_status(db, friend_request, status=REJECTED)
    await realtime_manager.send_to_user(
        friend_request.sender_id,
        {
            "type": "request:rejected",
            "request": serialize_friend_request(friend_request).model_dump(mode="json"),
            "message": f"{current_user.name} declined your match request.",
        },
    )
    return serialize_friend_request(friend_request)


@router.get("/friends", response_model=schemas.FriendsResponse)
def get_friends(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    overview = build_friend_overview(db, current_user, online_user_ids=realtime_manager.online_user_ids())
    return schemas.FriendsResponse(
        friends=[schemas.FriendResponse(**item) for item in overview["friends"]],
        incoming_requests=[serialize_friend_request(item) for item in overview["incoming_requests"]],
        outgoing_requests=[serialize_friend_request(item) for item in overview["outgoing_requests"]],
        followers=[serialize_user_mini(item) for item in overview["followers"]],
        following=[serialize_user_mini(item) for item in overview["following"]],
    )


@router.get("/messages/{user_id}", response_model=schemas.ConversationResponse)
async def get_messages(
    user_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    other_user = get_user_or_none(db, user_id)
    if not other_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if not are_friends(db, current_user.id, other_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only chat with accepted connections.")

    read_ids = mark_messages_as_read(db, reader_id=current_user.id, other_user_id=other_user.id)
    if read_ids:
        await realtime_manager.send_to_user(
            other_user.id,
            {
                "type": "message:read",
                "message_ids": read_ids,
                "user_id": current_user.id,
            },
        )

    messages = get_messages_between_users(db, current_user.id, other_user.id)
    return schemas.ConversationResponse(
        conversation_with=serialize_user_mini(other_user),
        messages=[serialize_message(message, current_user.id) for message in messages],
    )


@router.post("/messages/{user_id}/attachments", response_model=schemas.MessageResponse, status_code=status.HTTP_201_CREATED)
async def upload_chat_attachment(
    user_id: int,
    file: UploadFile = File(...),
    content: str = Form(default=""),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    other_user = get_user_or_none(db, user_id)
    if not other_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if not are_friends(db, current_user.id, other_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only message accepted connections.")

    data = await file.read()
    if len(data) > 5_000_000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Attachments must be smaller than 5MB.")

    message_type = "image" if (file.content_type or "").startswith("image/") else "file"
    message = create_message(
        db,
        current_user,
        other_user,
        content,
        message_type=message_type,
        attachment_filename=file.filename,
        attachment_content_type=file.content_type,
        attachment_data=data,
    )

    payload = serialize_message(message, current_user.id).model_dump(mode="json")
    incoming = serialize_message(message, other_user.id).model_dump(mode="json")
    await realtime_manager.send_to_user(current_user.id, {"type": "message:new", "message": payload, "with_user": serialize_user_mini(other_user).model_dump(mode="json")})
    await realtime_manager.send_to_user(other_user.id, {"type": "message:new", "message": incoming, "with_user": serialize_user_mini(current_user).model_dump(mode="json")})
    return serialize_message(message, current_user.id)


@router.get("/messages/attachments/{message_id}")
def get_message_attachment(
    message_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    message = db.get(models.Message, message_id)
    if not message or not message.attachment_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found.")
    if current_user.id not in {message.sender_id, message.receiver_id}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot access this attachment.")
    return Response(content=message.attachment_data, media_type=message.attachment_content_type)


@router.post("/follow/{user_id}", response_model=schemas.FollowResponse)
def follow_profile(user_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot follow yourself.")
    target = get_user_or_none(db, user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    follow_user(db, follower=current_user, followed=target)
    return schemas.FollowResponse(following=True, user_id=user_id)


@router.delete("/follow/{user_id}", response_model=schemas.FollowResponse)
def unfollow_profile(user_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    removed = unfollow_user(db, follower_id=current_user.id, followed_id=user_id)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Follow relationship not found.")
    return schemas.FollowResponse(following=False, user_id=user_id)


@router.post("/reviews", response_model=schemas.ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review_route(
    payload: schemas.ReviewCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.reviewee_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot review yourself.")

    reviewee = get_user_or_none(db, payload.reviewee_id)
    if not reviewee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if not are_friends(db, current_user.id, reviewee.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Reviews are only available after a real connection.")

    review = create_review(
        db,
        reviewer=current_user,
        reviewee=reviewee,
        rating=payload.rating,
        comment=payload.comment,
        endorsement=payload.endorsement,
    )
    return schemas.ReviewResponse(
        id=review.id,
        reviewer=serialize_user_mini(current_user),
        reviewee_id=review.reviewee_id,
        rating=review.rating,
        comment=review.comment,
        endorsement=review.endorsement,
        created_at=review.created_at,
    )

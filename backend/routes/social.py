from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..models import User
from ..schemas import (
    ConversationResponse,
    FriendRequestAction,
    FriendRequestCreate,
    FriendRequestResponse,
    FriendsResponse,
    MessageResponse,
    UserMini,
)
from ..services.realtime import realtime_manager
from ..services.social import (
    ACCEPTED,
    PENDING,
    REJECTED,
    are_friends,
    build_friend_overview,
    create_friend_request,
    get_friend_request_or_none,
    get_friendship_request_between,
    get_messages_between_users,
    get_user_or_none,
    mark_messages_as_read,
    update_friend_request_status,
)
from ..database import get_db

router = APIRouter(tags=["Social"])


def serialize_friend_request(friend_request) -> FriendRequestResponse:
    return FriendRequestResponse(
        id=friend_request.id,
        sender=UserMini.model_validate(friend_request.sender),
        receiver=UserMini.model_validate(friend_request.receiver),
        status=friend_request.status,
        created_at=friend_request.created_at,
        updated_at=friend_request.updated_at,
    )


@router.post("/send-request", response_model=FriendRequestResponse, status_code=status.HTTP_201_CREATED)
async def send_request(
    payload: FriendRequestCreate,
    current_user: User = Depends(get_current_user),
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


@router.post("/accept-request", response_model=FriendRequestResponse)
async def accept_request(
    payload: FriendRequestAction,
    current_user: User = Depends(get_current_user),
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
    await realtime_manager.send_to_user(
        friend_request.receiver_id,
        {
            "type": "request:accepted",
            "request": serialize_friend_request(friend_request).model_dump(mode="json"),
            "message": f"You are now connected with {friend_request.sender.name}.",
        },
    )

    return serialize_friend_request(friend_request)


@router.post("/reject-request", response_model=FriendRequestResponse)
async def reject_request(
    payload: FriendRequestAction,
    current_user: User = Depends(get_current_user),
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


@router.get("/friends", response_model=FriendsResponse)
def get_friends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    overview = build_friend_overview(db, current_user)
    return FriendsResponse(
        friends=overview["friends"],
        incoming_requests=[serialize_friend_request(item) for item in overview["incoming_requests"]],
        outgoing_requests=[serialize_friend_request(item) for item in overview["outgoing_requests"]],
    )


@router.get("/messages/{user_id}", response_model=ConversationResponse)
def get_messages(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    other_user = get_user_or_none(db, user_id)
    if not other_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if not are_friends(db, current_user.id, other_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only chat with accepted connections.")

    mark_messages_as_read(db, reader_id=current_user.id, other_user_id=other_user.id)
    messages = get_messages_between_users(db, current_user.id, other_user.id)

    return ConversationResponse(
        conversation_with=UserMini.model_validate(other_user),
        messages=[
            MessageResponse(
                id=message.id,
                sender_id=message.sender_id,
                receiver_id=message.receiver_id,
                content=message.content,
                created_at=message.created_at,
                read_at=message.read_at,
                is_mine=message.sender_id == current_user.id,
            )
            for message in messages
        ],
    )

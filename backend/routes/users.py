from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db
from ..services.dashboard import build_dashboard_summary
from ..services.notifications import list_notifications, mark_notification_read
from ..services.social import are_friends
from ..services.users import (
    ensure_profile,
    get_user_with_profile,
    search_users,
    serialize_user,
    serialize_user_mini,
    set_profile_avatar,
    update_profile,
)

router = APIRouter(tags=["Users"])


def get_friend_count(db: Session, user_id: int) -> int:
    return db.execute(
        select(func.count(models.FriendRequest.id)).where(
            models.FriendRequest.status == "accepted",
            or_(
                models.FriendRequest.sender_id == user_id,
                models.FriendRequest.receiver_id == user_id,
            ),
        )
    ).scalar_one()


def require_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return current_user


@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = get_user_with_profile(db, current_user.id) or current_user
    ensure_profile(db, user)
    user = get_user_with_profile(db, user.id) or user
    return serialize_user(user, friends_count=get_friend_count(db, user.id))


@router.patch("/profile", response_model=schemas.UserResponse)
def patch_profile(
    payload: schemas.UpdateProfileRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = update_profile(db, current_user, payload)
    return serialize_user(user, friends_count=get_friend_count(db, user.id))


@router.post("/profile/avatar", response_model=schemas.UserResponse)
async def upload_avatar(
    avatar: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if avatar.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only JPEG, PNG, and WEBP avatars are supported.")

    data = await avatar.read()
    if not data or len(data) > 2_500_000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Avatar file must be smaller than 2.5MB.")

    user = set_profile_avatar(
        db,
        current_user,
        filename=avatar.filename or "avatar",
        content_type=avatar.content_type,
        data=data,
    )
    return serialize_user(user, friends_count=get_friend_count(db, user.id))


@router.get("/profile/avatar/{user_id}")
def get_avatar(user_id: int, db: Session = Depends(get_db)):
    user = get_user_with_profile(db, user_id)
    if not user or not user.profile or not user.profile.avatar_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found.")
    return Response(content=user.profile.avatar_data, media_type=user.profile.avatar_content_type)


@router.get("/dashboard/summary", response_model=schemas.DashboardSummaryResponse)
def dashboard_summary(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = get_user_with_profile(db, current_user.id) or current_user
    ensure_profile(db, user)
    user = get_user_with_profile(db, user.id) or user
    return build_dashboard_summary(db, user)


@router.get("/notifications", response_model=list[schemas.NotificationResponse])
def get_notifications(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [schemas.NotificationResponse.model_validate(item) for item in list_notifications(db, user_id=current_user.id)]


@router.post("/notifications/{notification_id}/read", response_model=schemas.NotificationResponse)
def read_notification(
    notification_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification = mark_notification_read(db, notification_id=notification_id, user_id=current_user.id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
    return schemas.NotificationResponse.model_validate(notification)


@router.get("/users/discover", response_model=schemas.DiscoverUsersResponse)
def discover_users(
    query: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=50),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    users, total = search_users(db, current_user_id=current_user.id, query=query, page=page, page_size=page_size)
    return schemas.DiscoverUsersResponse(
        items=[serialize_user_mini(user) for user in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/admin/summary", response_model=schemas.AdminSummaryResponse)
def admin_summary(_admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    return schemas.AdminSummaryResponse(
        total_users=db.execute(select(func.count(models.User.id))).scalar_one(),
        verified_users=db.execute(select(func.count(models.User.id)).where(models.User.is_verified.is_(True))).scalar_one(),
        open_learning_requests=db.execute(
            select(func.count(models.LearningRequest.id)).where(models.LearningRequest.status == "open")
        ).scalar_one(),
        pending_friend_requests=db.execute(
            select(func.count(models.FriendRequest.id)).where(models.FriendRequest.status == "pending")
        ).scalar_one(),
        total_messages=db.execute(select(func.count(models.Message.id))).scalar_one(),
    )


@router.patch("/admin/users/{user_id}", response_model=schemas.UserResponse)
def admin_update_user(
    user_id: int,
    payload: schemas.AdminUserUpdate,
    _admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = get_user_with_profile(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if payload.is_admin is not None:
        user.is_admin = payload.is_admin
    if payload.is_verified is not None:
        user.is_verified = payload.is_verified

    db.add(user)
    db.commit()
    db.refresh(user)
    return serialize_user(user, friends_count=get_friend_count(db, user.id))


@router.get("/admin/users", response_model=schemas.DiscoverUsersResponse)
def admin_list_users(
    query: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    users, total = search_users(
        db,
        current_user_id=0,
        query=query,
        page=page,
        page_size=page_size,
    )
    return schemas.DiscoverUsersResponse(
        items=[serialize_user_mini(user) for user in users],
        total=total,
        page=page,
        page_size=page_size,
    )

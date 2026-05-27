from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db
from ..services.marketplace import (
    create_application,
    create_learning_request,
    get_learning_request_or_404,
    list_learning_requests,
    serialize_learning_request,
    update_learning_request,
)
from ..services.users import serialize_user_mini

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


@router.get("/requests", response_model=schemas.PaginatedLearningRequestsResponse)
def get_learning_requests(
    query: str = Query(default=""),
    status_filter: str = Query(default="", alias="status"),
    skill: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=50),
    _current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, total = list_learning_requests(
        db,
        query=query,
        status=status_filter,
        skill_slug=skill,
        page=page,
        page_size=page_size,
    )
    return schemas.PaginatedLearningRequestsResponse(
        items=[serialize_learning_request(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/requests", response_model=schemas.LearningRequestResponse, status_code=status.HTTP_201_CREATED)
def post_learning_request(
    payload: schemas.LearningRequestCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = create_learning_request(db, user=current_user, payload=payload)
    return serialize_learning_request(item)


@router.patch("/requests/{request_id}", response_model=schemas.LearningRequestResponse)
def patch_learning_request(
    request_id: int,
    payload: schemas.LearningRequestUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = get_learning_request_or_404(db, request_id)
    if item.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own requests.")
    updated = update_learning_request(db, learning_request=item, payload=payload)
    return serialize_learning_request(updated)


@router.post("/requests/{request_id}/apply", response_model=schemas.LearningRequestApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_to_learning_request(
    request_id: int,
    payload: schemas.LearningRequestApplicationCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = get_learning_request_or_404(db, request_id)
    if item.creator_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot apply to your own learning request.")

    application = create_application(db, learning_request=item, applicant=current_user, message=payload.message)
    return schemas.LearningRequestApplicationResponse(
        id=application.id,
        applicant=serialize_user_mini(current_user),
        status=application.status,
        message=application.message,
        created_at=application.created_at,
    )

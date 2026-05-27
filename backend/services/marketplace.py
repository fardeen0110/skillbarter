from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas
from .notifications import create_notification
from .users import get_skills_by_names, serialize_user_mini


def get_skill_by_name(db: Session, name: str) -> models.Skill:
    skill = get_skills_by_names(db, [name])[0]
    return skill


def create_learning_request(
    db: Session,
    *,
    user: models.User,
    payload: schemas.LearningRequestCreate,
) -> models.LearningRequest:
    skill = get_skill_by_name(db, payload.skill)
    learning_request = models.LearningRequest(
        creator_id=user.id,
        skill_id=skill.id,
        title=payload.title.strip(),
        description=payload.description.strip(),
        city=payload.city.strip(),
        availability=payload.availability.strip(),
        status="open",
    )
    db.add(learning_request)
    db.commit()
    db.refresh(learning_request)
    return get_learning_request_or_404(db, learning_request.id)


def get_learning_request_or_404(db: Session, request_id: int) -> models.LearningRequest:
    learning_request = db.execute(
        select(models.LearningRequest)
        .options(
            joinedload(models.LearningRequest.creator).joinedload(models.User.profile),
            joinedload(models.LearningRequest.skill),
            joinedload(models.LearningRequest.applications)
            .joinedload(models.LearningRequestApplication.applicant)
            .joinedload(models.User.profile),
        )
        .where(models.LearningRequest.id == request_id)
    ).unique().scalar_one()
    return learning_request


def update_learning_request(
    db: Session,
    *,
    learning_request: models.LearningRequest,
    payload: schemas.LearningRequestUpdate,
) -> models.LearningRequest:
    for field in ("title", "description", "city", "availability", "status"):
        value = getattr(payload, field)
        if value is not None:
            setattr(learning_request, field, value.strip() if isinstance(value, str) else value)

    db.add(learning_request)
    db.commit()
    db.refresh(learning_request)
    return get_learning_request_or_404(db, learning_request.id)


def create_application(
    db: Session,
    *,
    learning_request: models.LearningRequest,
    applicant: models.User,
    message: str,
) -> models.LearningRequestApplication:
    existing = db.execute(
        select(models.LearningRequestApplication).where(
            models.LearningRequestApplication.request_id == learning_request.id,
            models.LearningRequestApplication.applicant_id == applicant.id,
        )
    ).scalar_one_or_none()
    if existing:
        return existing

    application = models.LearningRequestApplication(
        request_id=learning_request.id,
        applicant_id=applicant.id,
        message=message.strip(),
        status="pending",
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    create_notification(
        db,
        user_id=learning_request.creator_id,
        notification_type="learning_request_application",
        title=f"{applicant.name} applied to your request",
        body=learning_request.title,
        link_url="/dashboard",
    )
    return application


def list_learning_requests(
    db: Session,
    *,
    query: str = "",
    status: str = "",
    skill_slug: str = "",
    page: int = 1,
    page_size: int = 12,
) -> tuple[list[models.LearningRequest], int]:
    base = (
        select(models.LearningRequest)
        .options(
            joinedload(models.LearningRequest.creator).joinedload(models.User.profile),
            joinedload(models.LearningRequest.skill),
            joinedload(models.LearningRequest.applications)
            .joinedload(models.LearningRequestApplication.applicant)
            .joinedload(models.User.profile),
        )
        .order_by(models.LearningRequest.created_at.desc(), models.LearningRequest.id.desc())
    )
    if query.strip():
        like = f"%{query.strip().lower()}%"
        base = base.where(
            func.lower(models.LearningRequest.title).like(like)
            | func.lower(models.LearningRequest.description).like(like)
            | func.lower(models.LearningRequest.city).like(like)
        )
    if status.strip():
        base = base.where(models.LearningRequest.status == status.strip().lower())
    if skill_slug.strip():
        base = base.join(models.LearningRequest.skill).where(models.Skill.slug == skill_slug.strip().lower())

    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    items = list(
        db.execute(base.offset((page - 1) * page_size).limit(page_size)).unique().scalars().all()
    )
    return items, total


def serialize_learning_request(request: models.LearningRequest) -> schemas.LearningRequestResponse:
    return schemas.LearningRequestResponse(
        id=request.id,
        title=request.title,
        description=request.description,
        city=request.city,
        availability=request.availability,
        status=request.status,
        created_at=request.created_at,
        updated_at=request.updated_at,
        creator=serialize_user_mini(request.creator),
        skill=schemas.SkillResponse.model_validate(request.skill),
        applications_count=len(request.applications),
        applications=[
            schemas.LearningRequestApplicationResponse(
                id=application.id,
                applicant=serialize_user_mini(application.applicant),
                status=application.status,
                message=application.message,
                created_at=application.created_at,
            )
            for application in request.applications
        ],
    )

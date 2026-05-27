from __future__ import annotations

import re
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas
from .storage import upload_file

DEFAULT_SKILLS = [
    ("React", "engineering"),
    ("Python", "engineering"),
    ("Node.js", "engineering"),
    ("Figma", "design"),
    ("UI Design", "design"),
    ("Graphic Design", "design"),
    ("Product Strategy", "product"),
    ("Project Management", "product"),
    ("Growth Marketing", "marketing"),
    ("SEO", "marketing"),
    ("Content Writing", "marketing"),
    ("Data Analysis", "analytics"),
    ("SQL", "analytics"),
    ("Public Speaking", "communication"),
    ("Pitch Decks", "communication"),
    ("Career Coaching", "coaching"),
    ("No-Code Automation", "automation"),
    ("AI Workflow Design", "automation"),
    ("Video Editing", "media"),
    ("Motion Design", "media"),
]


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return value.strip("-")


def ensure_profile(db: Session, user: models.User) -> models.UserProfile:
    if user.profile:
        return user.profile

    profile = models.UserProfile(user_id=user.id)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    db.refresh(user)
    return profile


def ensure_skill_catalog(db: Session) -> list[models.Skill]:
    existing_count = db.execute(select(func.count(models.Skill.id))).scalar_one()
    if existing_count:
        return list(db.execute(select(models.Skill).order_by(models.Skill.name.asc())).scalars())

    for name, category in DEFAULT_SKILLS:
        db.add(models.Skill(name=name, slug=slugify(name), category=category))

    db.commit()
    return list(db.execute(select(models.Skill).order_by(models.Skill.name.asc())).scalars())


def get_skills_by_names(db: Session, names: Sequence[str]) -> list[models.Skill]:
    ensure_skill_catalog(db)
    normalized_names = {name.strip().lower() for name in names if name.strip()}
    if not normalized_names:
        return []

    matched = list(db.execute(select(models.Skill).where(func.lower(models.Skill.name).in_(normalized_names))).scalars())
    existing_names = {skill.name.lower() for skill in matched}

    for name in normalized_names - existing_names:
        new_skill = models.Skill(name=name.title(), slug=slugify(name), category="general")
        db.add(new_skill)
        db.flush()
        matched.append(new_skill)

    db.commit()
    return sorted(matched, key=lambda item: item.name.lower())


def set_user_skills(
    db: Session,
    user: models.User,
    *,
    offered: Sequence[str],
    wanted: Sequence[str],
) -> None:
    offered_skills = get_skills_by_names(db, offered)
    wanted_skills = get_skills_by_names(db, wanted)

    db.query(models.UserOfferedSkill).filter(models.UserOfferedSkill.user_id == user.id).delete()
    db.query(models.UserWantedSkill).filter(models.UserWantedSkill.user_id == user.id).delete()
    db.flush()

    for skill in offered_skills:
        db.add(models.UserOfferedSkill(user_id=user.id, skill_id=skill.id))
    for skill in wanted_skills:
        db.add(models.UserWantedSkill(user_id=user.id, skill_id=skill.id))

    db.commit()
    db.refresh(user)


def update_profile(db: Session, user: models.User, payload: schemas.UpdateProfileRequest) -> models.User:
    profile = ensure_profile(db, user)
    user.name = payload.name.strip()
    profile.bio = payload.bio.strip()
    profile.city = payload.city.strip()
    profile.availability = payload.availability.strip()
    profile.experience_level = payload.experience_level.strip().lower() or "intermediate"
    profile.linkedin_url = payload.linkedin.strip()
    profile.website_url = payload.website.strip()
    profile.x_url = payload.x.strip()

    db.add(user)
    db.add(profile)
    db.commit()
    db.refresh(user)

    set_user_skills(db, user, offered=payload.skills_offered, wanted=payload.skills_wanted)
    user.last_active_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    db.refresh(user)
    return get_user_with_profile(db, user.id) or user


def set_profile_avatar(
    db: Session,
    user: models.User,
    *,
    filename: str,
    content_type: str,
    data: bytes,
) -> models.User:
    profile = ensure_profile(db, user)
    stored_asset = upload_file(
        data=data,
        content_type=content_type,
        folder="avatars",
        filename=filename,
    )
    profile.avatar_filename = filename
    profile.avatar_content_type = content_type
    profile.avatar_storage_path = stored_asset.storage_path if stored_asset else None
    profile.avatar_public_url = stored_asset.public_url if stored_asset else None
    profile.avatar_data = None if stored_asset else data
    db.add(profile)
    db.commit()
    db.refresh(user)
    return get_user_with_profile(db, user.id) or user


def get_user_with_profile(db: Session, user_id: int) -> models.User | None:
    statement = (
        select(models.User)
        .options(
            joinedload(models.User.profile),
            joinedload(models.User.offered_skills).joinedload(models.UserOfferedSkill.skill),
            joinedload(models.User.wanted_skills).joinedload(models.UserWantedSkill.skill),
            joinedload(models.User.followers),
            joinedload(models.User.following),
        )
        .where(models.User.id == user_id)
    )
    return db.execute(statement).unique().scalar_one_or_none()


def get_avatar_url(user: models.User) -> str | None:
    if user.profile and user.profile.avatar_public_url:
        return user.profile.avatar_public_url
    if user.profile and user.profile.avatar_data:
        return f"/profile/avatar/{user.id}"
    return None


def serialize_user_mini(user: models.User) -> schemas.UserMini:
    profile = user.profile
    return schemas.UserMini(
        id=user.id,
        name=user.name,
        email=user.email,
        avatar_url=get_avatar_url(user),
        city=profile.city if profile else "",
        rating_average=round(profile.rating_average, 2) if profile else 0,
    )


def serialize_user(user: models.User, *, friends_count: int = 0) -> schemas.UserResponse:
    profile = user.profile or models.UserProfile(
        bio="",
        city="",
        availability="",
        experience_level="intermediate",
        linkedin_url="",
        website_url="",
        x_url="",
        rating_average=0,
        rating_count=0,
    )

    return schemas.UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
        is_verified=user.is_verified,
        is_admin=user.is_admin,
        friends_count=friends_count,
        followers_count=len(user.followers),
        following_count=len(user.following),
        profile=schemas.ProfileResponse(
            bio=profile.bio,
            city=profile.city,
            availability=profile.availability,
            experience_level=profile.experience_level,
            rating_average=round(profile.rating_average, 2),
            rating_count=profile.rating_count,
            avatar_url=get_avatar_url(user),
            social_links=schemas.SocialLinksResponse(
                linkedin=profile.linkedin_url,
                website=profile.website_url,
                x=profile.x_url,
            ),
            skills_offered=[schemas.SkillResponse.model_validate(item.skill) for item in user.offered_skills],
            skills_wanted=[schemas.SkillResponse.model_validate(item.skill) for item in user.wanted_skills],
        ),
    )


def search_users(
    db: Session,
    *,
    current_user_id: int,
    query: str = "",
    page: int = 1,
    page_size: int = 12,
) -> tuple[list[models.User], int]:
    statement = (
        select(models.User)
        .options(joinedload(models.User.profile))
        .where(models.User.id != current_user_id)
        .order_by(models.User.last_active_at.desc(), models.User.created_at.desc())
    )

    if query.strip():
        like = f"%{query.strip().lower()}%"
        statement = statement.where(
            or_(
                func.lower(models.User.name).like(like),
                func.lower(models.User.email).like(like),
                func.lower(models.UserProfile.city).like(like),
            )
        ).join(models.User.profile, isouter=True)

    total = db.execute(select(func.count()).select_from(statement.subquery())).scalar_one()
    items = list(
        db.execute(statement.offset((page - 1) * page_size).limit(page_size)).scalars().unique().all()
    )
    return items, total

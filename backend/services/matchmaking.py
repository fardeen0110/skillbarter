from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, joinedload

from .. import models
from .users import ensure_skill_catalog, serialize_user_mini, slugify


def get_supported_skills(db: Session) -> list[str]:
    return [skill.name for skill in ensure_skill_catalog(db)]


def normalize_skill(db: Session, skill_name: str) -> models.Skill:
    target_slug = slugify(skill_name)
    ensure_skill_catalog(db)
    skill = db.execute(select(models.Skill).where(models.Skill.slug == target_slug)).scalar_one_or_none()
    if not skill:
        raise ValueError(f"Unsupported skill '{skill_name}'.")
    return skill


def availability_overlap_score(current: str, candidate: str) -> float:
    if not current or not candidate:
        return 0.4

    current_tokens = {token.strip().lower() for token in current.replace("/", ",").split(",") if token.strip()}
    candidate_tokens = {token.strip().lower() for token in candidate.replace("/", ",").split(",") if token.strip()}
    if not current_tokens or not candidate_tokens:
        return 0.4

    overlap = current_tokens & candidate_tokens
    if overlap:
        return min(1.0, 0.5 + (len(overlap) * 0.2))
    return 0.25


def experience_score(level: str) -> float:
    mapping = {
        "beginner": 0.45,
        "intermediate": 0.72,
        "advanced": 0.88,
        "expert": 1.0,
    }
    return mapping.get(level.strip().lower(), 0.6)


def activity_score(last_active_at: datetime) -> float:
    if last_active_at.tzinfo is None:
        last_active_at = last_active_at.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    if last_active_at >= now - timedelta(days=2):
        return 1.0
    if last_active_at >= now - timedelta(days=7):
        return 0.8
    if last_active_at >= now - timedelta(days=21):
        return 0.55
    return 0.3


def get_top_matches(
    db: Session,
    skill_offer: str,
    skill_want: str,
    *,
    current_user_id: int,
    limit: int = 5,
) -> list[dict]:
    offered_skill = normalize_skill(db, skill_offer)
    wanted_skill = normalize_skill(db, skill_want)

    if offered_skill.id == wanted_skill.id:
        raise ValueError("Choose different skills for offer and want.")

    current_user = db.execute(
        select(models.User)
        .options(
            joinedload(models.User.profile),
            joinedload(models.User.offered_skills).joinedload(models.UserOfferedSkill.skill),
            joinedload(models.User.wanted_skills).joinedload(models.UserWantedSkill.skill),
        )
        .where(models.User.id == current_user_id)
    ).unique().scalar_one()

    current_profile = current_user.profile
    current_offered = {item.skill_id for item in current_user.offered_skills}
    current_wanted = {item.skill_id for item in current_user.wanted_skills}

    candidates = list(
        db.execute(
            select(models.User)
            .options(
                joinedload(models.User.profile),
                joinedload(models.User.offered_skills).joinedload(models.UserOfferedSkill.skill),
                joinedload(models.User.wanted_skills).joinedload(models.UserWantedSkill.skill),
                joinedload(models.User.followers),
            )
            .where(models.User.id != current_user_id)
            .order_by(models.User.last_active_at.desc(), models.User.created_at.desc())
        ).unique().scalars()
    )

    scored_matches: list[dict] = []
    for candidate in candidates:
        if not candidate.profile or not candidate.offered_skills:
            continue

        candidate_offered = {item.skill_id for item in candidate.offered_skills}
        candidate_wanted = {item.skill_id for item in candidate.wanted_skills}

        wants_my_offer = 1.0 if offered_skill.id in candidate_wanted else 0.25
        has_my_want = 1.0 if wanted_skill.id in candidate_offered else 0.25
        shared_interests = len(current_wanted & candidate_wanted) + len(current_offered & candidate_offered)
        complementary_bonus = 0.15 if offered_skill.id in candidate_wanted and wanted_skill.id in candidate_offered else 0.0
        shared_interest_score = min(1.0, 0.25 + (shared_interests * 0.15))
        rating_score = min(1.0, (candidate.profile.rating_average or 0) / 5) if candidate.profile.rating_count else 0.55
        availability_score = availability_overlap_score(
            current_profile.availability if current_profile else "",
            candidate.profile.availability,
        )
        activity = activity_score(candidate.last_active_at)
        experience = experience_score(candidate.profile.experience_level)
        social_proof = min(1.0, 0.4 + (len(candidate.followers) * 0.06))

        weighted_score = (
            (wants_my_offer * 0.25)
            + (has_my_want * 0.27)
            + (shared_interest_score * 0.12)
            + (rating_score * 0.12)
            + (availability_score * 0.10)
            + (activity * 0.08)
            + (experience * 0.04)
            + (social_proof * 0.02)
            + complementary_bonus
        )

        candidate_skill_name = next(
            (item.skill.name for item in candidate.offered_skills if item.skill_id == wanted_skill.id),
            candidate.offered_skills[0].skill.name,
        )

        shared_skill_names = sorted(
            {
                item.skill.name
                for item in candidate.offered_skills + candidate.wanted_skills
                if item.skill_id in current_offered or item.skill_id in current_wanted
            }
        )

        scored_matches.append(
            {
                "user_id": candidate.id,
                "name": candidate.name,
                "skill": candidate_skill_name,
                "city": candidate.profile.city,
                "rating_average": round(candidate.profile.rating_average, 2),
                "shared_skills": shared_skill_names[:3],
                "score": max(1, min(99, round(weighted_score * 100))),
            }
        )

    scored_matches.sort(key=lambda item: (item["score"], item["rating_average"], item["name"]), reverse=True)
    return scored_matches[:limit]

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from random import Random

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import User


@dataclass(frozen=True)
class SimulatedUser:
    email: str
    name: str
    skill_offer: str
    skill_want: str
    availability: float
    experience: float
    rating: float
    interaction_preference: float
    prior_exchange_count: int


SKILL_GROUPS = {
    "Python": "engineering",
    "React": "engineering",
    "Node.js": "engineering",
    "UI Design": "design",
    "Figma": "design",
    "Graphic Design": "design",
    "SEO": "marketing",
    "Content Writing": "marketing",
    "Growth Marketing": "marketing",
    "Video Editing": "media",
    "Motion Design": "media",
    "Public Speaking": "communication",
    "Pitch Decks": "communication",
    "Product Strategy": "product",
    "Project Management": "product",
    "Data Analysis": "analytics",
    "SQL": "analytics",
    "Career Coaching": "coaching",
    "English Speaking": "coaching",
    "No-Code Automation": "automation",
}

SIMULATED_USERS = [
    SimulatedUser("aarav.demo@skillbarter.app", "Aarav Mehta", "Python", "UI Design", 0.82, 4.5, 4.8, 0.86, 7),
    SimulatedUser("maya.demo@skillbarter.app", "Maya Chen", "React", "Product Strategy", 0.76, 4.0, 4.7, 0.80, 6),
    SimulatedUser("liam.demo@skillbarter.app", "Liam Brooks", "SEO", "Python", 0.71, 3.2, 4.5, 0.70, 4),
    SimulatedUser("priya.demo@skillbarter.app", "Priya Nair", "Figma", "React", 0.90, 5.0, 4.9, 0.92, 10),
    SimulatedUser("jon.demo@skillbarter.app", "Jon Rivera", "Motion Design", "Node.js", 0.65, 4.1, 4.4, 0.73, 3),
    SimulatedUser("sara.demo@skillbarter.app", "Sara Idris", "Data Analysis", "Public Speaking", 0.84, 4.6, 4.8, 0.88, 9),
    SimulatedUser("theo.demo@skillbarter.app", "Theo Marshall", "Public Speaking", "Data Analysis", 0.79, 4.7, 4.6, 0.82, 8),
    SimulatedUser("elena.demo@skillbarter.app", "Elena Garcia", "Video Editing", "Growth Marketing", 0.74, 3.9, 4.3, 0.69, 4),
    SimulatedUser("kaito.demo@skillbarter.app", "Kaito Mori", "Pitch Decks", "React", 0.68, 4.2, 4.5, 0.77, 5),
    SimulatedUser("nina.demo@skillbarter.app", "Nina Patel", "Growth Marketing", "Video Editing", 0.87, 4.4, 4.7, 0.84, 7),
    SimulatedUser("omar.demo@skillbarter.app", "Omar Hassan", "SQL", "Career Coaching", 0.73, 3.7, 4.2, 0.68, 2),
    SimulatedUser("ava.demo@skillbarter.app", "Ava Thompson", "Career Coaching", "SQL", 0.86, 4.8, 4.9, 0.91, 11),
    SimulatedUser("rohan.demo@skillbarter.app", "Rohan Kapoor", "Node.js", "Motion Design", 0.78, 4.0, 4.4, 0.75, 6),
    SimulatedUser("sofia.demo@skillbarter.app", "Sofia Martinez", "Graphic Design", "Content Writing", 0.69, 3.6, 4.1, 0.66, 2),
    SimulatedUser("marcus.demo@skillbarter.app", "Marcus Hale", "Product Strategy", "React", 0.83, 5.0, 4.8, 0.87, 9),
    SimulatedUser("isha.demo@skillbarter.app", "Isha Verma", "English Speaking", "No-Code Automation", 0.80, 3.8, 4.4, 0.78, 5),
    SimulatedUser("daniel.demo@skillbarter.app", "Daniel Kim", "No-Code Automation", "English Speaking", 0.92, 4.3, 4.8, 0.90, 10),
    SimulatedUser("ananya.demo@skillbarter.app", "Ananya Rao", "Content Writing", "Graphic Design", 0.77, 4.1, 4.5, 0.80, 6),
    SimulatedUser("lucas.demo@skillbarter.app", "Lucas White", "Project Management", "Pitch Decks", 0.72, 4.0, 4.3, 0.71, 4),
    SimulatedUser("zara.demo@skillbarter.app", "Zara Ali", "UI Design", "Python", 0.89, 4.7, 4.9, 0.93, 12),
]

ALL_SKILLS = sorted(SKILL_GROUPS.keys())
INTERACTION_OPTIONS = [0.25, 0.5, 0.75, 1.0]


def normalize_skill(skill: str) -> str:
    normalized = skill.strip().lower()
    for supported_skill in ALL_SKILLS:
        if supported_skill.lower() == normalized:
            return supported_skill
    raise ValueError(f"Unsupported skill '{skill}'.")


def get_supported_skills() -> list[str]:
    return ALL_SKILLS


def skill_similarity(skill_a: str, skill_b: str) -> float:
    if skill_a == skill_b:
        return 1.0
    if SKILL_GROUPS.get(skill_a) == SKILL_GROUPS.get(skill_b):
        return 0.7
    return 0.25


def compute_feature_vector(skill_offer: str, skill_want: str, candidate: SimulatedUser) -> list[float]:
    canonical_offer = normalize_skill(skill_offer)
    canonical_want = normalize_skill(skill_want)

    offer_alignment = skill_similarity(canonical_offer, candidate.skill_want)
    want_alignment = skill_similarity(canonical_want, candidate.skill_offer)
    combined_similarity = round((offer_alignment * 0.45) + (want_alignment * 0.55), 4)

    availability_overlap = candidate.availability
    experience_gap = min(abs(4.0 - candidate.experience) / 5.0, 1.0)
    user_rating_avg = candidate.rating / 5.0
    interaction_preference = candidate.interaction_preference
    prior_exchange_count = min(candidate.prior_exchange_count / 12.0, 1.0)

    return [
        combined_similarity,
        availability_overlap,
        experience_gap,
        user_rating_avg,
        interaction_preference,
        prior_exchange_count,
    ]


def build_synthetic_dataset(sample_count: int = 1000) -> tuple[list[list[float]], list[int]]:
    rng = Random(42)
    features: list[list[float]] = []
    targets: list[int] = []

    for _ in range(sample_count):
        skill_offer = rng.choice(ALL_SKILLS)
        skill_want = rng.choice(ALL_SKILLS)
        candidate = SimulatedUser(
            email="synthetic-user@skillbarter.app",
            name="Synthetic User",
            skill_offer=rng.choice(ALL_SKILLS),
            skill_want=rng.choice(ALL_SKILLS),
            availability=rng.uniform(0.35, 1.0),
            experience=rng.uniform(1.0, 5.0),
            rating=rng.uniform(3.0, 5.0),
            interaction_preference=rng.choice(INTERACTION_OPTIONS),
            prior_exchange_count=rng.randint(0, 12),
        )
        row = compute_feature_vector(skill_offer, skill_want, candidate)
        weighted_score = (
            (row[0] * 0.34)
            + (row[1] * 0.18)
            + ((1 - row[2]) * 0.14)
            + (row[3] * 0.16)
            + (row[4] * 0.08)
            + (row[5] * 0.10)
            + rng.uniform(-0.06, 0.06)
        )
        targets.append(1 if weighted_score >= 0.61 else 0)
        features.append(row)

    return features, targets


@dataclass(frozen=True)
class MatchmakingArtifacts:
    logistic_model: LogisticRegression
    random_forest_model: RandomForestClassifier
    users: list[SimulatedUser]


@lru_cache(maxsize=1)
def get_matchmaking_artifacts() -> MatchmakingArtifacts:
    features, targets = build_synthetic_dataset()

    logistic_model = LogisticRegression(max_iter=1000, random_state=42)
    logistic_model.fit(features, targets)

    random_forest_model = RandomForestClassifier(
        n_estimators=240,
        max_depth=10,
        min_samples_split=4,
        random_state=42,
    )
    random_forest_model.fit(features, targets)

    return MatchmakingArtifacts(
        logistic_model=logistic_model,
        random_forest_model=random_forest_model,
        users=SIMULATED_USERS,
    )


def get_top_matches(
    db: Session,
    skill_offer: str,
    skill_want: str,
    *,
    current_user_id: int,
    limit: int = 5,
) -> list[dict]:
    canonical_offer = normalize_skill(skill_offer)
    canonical_want = normalize_skill(skill_want)

    if canonical_offer == canonical_want:
        raise ValueError("Choose different skills for offer and want.")

    artifacts = get_matchmaking_artifacts()
    scored_matches: list[dict] = []

    for user in artifacts.users:
        user_record = db.execute(select(User).where(User.email == user.email)).scalar_one_or_none()
        if not user_record or user_record.id == current_user_id:
            continue
        row = compute_feature_vector(canonical_offer, canonical_want, user)
        model_probability = artifacts.random_forest_model.predict_proba([row])[0][1]
        reciprocal_bonus = 0.08 if user.skill_want == canonical_offer else 0.0
        relevance_score = min(0.99, model_probability + reciprocal_bonus)
        score = max(1, min(99, round(relevance_score * 100)))
        scored_matches.append(
            {
                "user_id": user_record.id,
                "name": user_record.name,
                "skill": user.skill_offer,
                "score": score,
            }
        )

    scored_matches.sort(key=lambda match: (match["score"], match["name"]), reverse=True)
    return scored_matches[:limit]

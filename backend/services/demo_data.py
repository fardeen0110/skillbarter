from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import hash_password
from ..models import User

DEMO_USERS = [
    {"name": "Aarav Mehta", "email": "aarav.demo@skillbarter.app"},
    {"name": "Maya Chen", "email": "maya.demo@skillbarter.app"},
    {"name": "Liam Brooks", "email": "liam.demo@skillbarter.app"},
    {"name": "Priya Nair", "email": "priya.demo@skillbarter.app"},
    {"name": "Jon Rivera", "email": "jon.demo@skillbarter.app"},
    {"name": "Sara Idris", "email": "sara.demo@skillbarter.app"},
    {"name": "Theo Marshall", "email": "theo.demo@skillbarter.app"},
    {"name": "Elena Garcia", "email": "elena.demo@skillbarter.app"},
    {"name": "Kaito Mori", "email": "kaito.demo@skillbarter.app"},
    {"name": "Nina Patel", "email": "nina.demo@skillbarter.app"},
    {"name": "Omar Hassan", "email": "omar.demo@skillbarter.app"},
    {"name": "Ava Thompson", "email": "ava.demo@skillbarter.app"},
    {"name": "Rohan Kapoor", "email": "rohan.demo@skillbarter.app"},
    {"name": "Sofia Martinez", "email": "sofia.demo@skillbarter.app"},
    {"name": "Marcus Hale", "email": "marcus.demo@skillbarter.app"},
    {"name": "Isha Verma", "email": "isha.demo@skillbarter.app"},
    {"name": "Daniel Kim", "email": "daniel.demo@skillbarter.app"},
    {"name": "Ananya Rao", "email": "ananya.demo@skillbarter.app"},
    {"name": "Lucas White", "email": "lucas.demo@skillbarter.app"},
    {"name": "Zara Ali", "email": "zara.demo@skillbarter.app"},
]


def seed_demo_users(db: Session) -> None:
    existing_emails = set(db.execute(select(User.email)).scalars().all())
    created = False

    for demo_user in DEMO_USERS:
        if demo_user["email"] in existing_emails:
            continue

        db.add(
            User(
                name=demo_user["name"],
                email=demo_user["email"],
                password_hash=hash_password("demo-user-password"),
            )
        )
        created = True

    if created:
        db.commit()

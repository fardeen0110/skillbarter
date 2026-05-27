from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_raw_token() -> str:
    return secrets.token_urlsafe(32)


def create_password_reset_token(db: Session, user: models.User, *, expires_in_minutes: int = 30) -> str:
    raw_token = generate_raw_token()
    hashed = hash_token(raw_token)

    db.add(
        models.PasswordResetToken(
            user_id=user.id,
            token_hash=hashed,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes),
        )
    )
    db.commit()
    return raw_token


def consume_password_reset_token(db: Session, raw_token: str) -> models.PasswordResetToken | None:
    token = db.execute(
        select(models.PasswordResetToken).where(models.PasswordResetToken.token_hash == hash_token(raw_token))
    ).scalar_one_or_none()
    if not token:
        return None
    if token.used_at is not None or token.expires_at <= datetime.now(timezone.utc):
        return None
    token.used_at = datetime.now(timezone.utc)
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def create_email_verification_token(db: Session, user: models.User, *, expires_in_hours: int = 48) -> str:
    raw_token = generate_raw_token()
    hashed = hash_token(raw_token)

    db.add(
        models.EmailVerificationToken(
            user_id=user.id,
            token_hash=hashed,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=expires_in_hours),
        )
    )
    db.commit()
    return raw_token


def consume_email_verification_token(db: Session, raw_token: str) -> models.EmailVerificationToken | None:
    token = db.execute(
        select(models.EmailVerificationToken).where(models.EmailVerificationToken.token_hash == hash_token(raw_token))
    ).scalar_one_or_none()
    if not token:
        return None
    if token.used_at is not None or token.expires_at <= datetime.now(timezone.utc):
        return None
    token.used_at = datetime.now(timezone.utc)
    db.add(token)
    db.commit()
    db.refresh(token)
    return token

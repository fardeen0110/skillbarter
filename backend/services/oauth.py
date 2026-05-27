from __future__ import annotations

import secrets
from urllib.parse import urlencode

import httpx
from authlib.integrations.httpx_client import AsyncOAuth2Client
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import auth, models
from ..config import get_settings
from .users import ensure_profile

settings = get_settings()
GOOGLE_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


def sanitize_next_path(next_path: str | None) -> str:
    candidate = (next_path or "").strip()
    if not candidate.startswith("/") or candidate.startswith("//"):
        return "/dashboard"
    return candidate


def build_oauth_redirect_uri(provider: str) -> str:
    return f"{settings.oauth_redirect_base_url.rstrip('/')}/oauth/{provider}/callback"


def build_google_authorize_url(next_path: str = "/dashboard") -> str:
    state = auth.create_oauth_state_token("google", next_path=sanitize_next_path(next_path))
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": build_oauth_redirect_uri("google"),
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
        "prompt": "select_account",
        "include_granted_scopes": "true",
        "state": state,
    }
    return f"{GOOGLE_AUTHORIZE_URL}?{urlencode(params)}"


def build_github_authorize_url(next_path: str = "/dashboard") -> str:
    state = auth.create_oauth_state_token("github", next_path=sanitize_next_path(next_path))
    params = {
        "client_id": settings.github_client_id,
        "redirect_uri": build_oauth_redirect_uri("github"),
        "scope": "read:user user:email",
        "state": state,
    }
    return f"https://github.com/login/oauth/authorize?{urlencode(params)}"


async def exchange_google_code(code: str) -> dict:
    async with AsyncOAuth2Client(
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        redirect_uri=build_oauth_redirect_uri("google"),
    ) as client:
        token = await client.fetch_token(
            GOOGLE_TOKEN_URL,
            code=code,
            grant_type="authorization_code",
        )
        response = await client.get(GOOGLE_USERINFO_URL, token=token)
        response.raise_for_status()
        return response.json()


def exchange_github_code(code: str) -> dict:
    response = httpx.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": settings.github_client_id,
            "client_secret": settings.github_client_secret,
            "code": code,
            "redirect_uri": build_oauth_redirect_uri("github"),
        },
        timeout=20,
    )
    response.raise_for_status()
    token_data = response.json()
    profile = httpx.get(
        "https://api.github.com/user",
        headers={
            "Authorization": f"Bearer {token_data['access_token']}",
            "Accept": "application/vnd.github+json",
        },
        timeout=20,
    )
    profile.raise_for_status()
    emails = httpx.get(
        "https://api.github.com/user/emails",
        headers={
            "Authorization": f"Bearer {token_data['access_token']}",
            "Accept": "application/vnd.github+json",
        },
        timeout=20,
    )
    emails.raise_for_status()
    primary_email = next((item["email"] for item in emails.json() if item.get("primary")), "")
    data = profile.json()
    data["email"] = data.get("email") or primary_email
    return data


def upsert_oauth_user(
    db: Session,
    *,
    provider: str,
    provider_user_id: str,
    email: str,
    name: str,
    avatar_url: str | None = None,
) -> models.User:
    normalized_email = email.strip().lower()
    account = db.execute(
        select(models.OAuthAccount)
        .where(models.OAuthAccount.provider == provider, models.OAuthAccount.provider_user_id == provider_user_id)
    ).scalar_one_or_none()
    if account:
        user = db.get(models.User, account.user_id)
        if user:
            profile = ensure_profile(db, user)
            user.name = name.strip() or user.name
            user.is_verified = True
            account.provider_email = normalized_email
            if avatar_url:
                profile.avatar_public_url = avatar_url
            db.add(account)
            db.add(user)
            db.add(profile)
            db.commit()
            db.refresh(user)
            return user

    user = auth.get_user_by_email(db, normalized_email)
    if not user:
        user = models.User(
            name=name.strip() or normalized_email.split("@")[0],
            email=normalized_email,
            password_hash=auth.hash_password(secrets.token_urlsafe(32)),
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.name = name.strip() or user.name
        user.is_verified = True

    profile = ensure_profile(db, user)
    if avatar_url:
        profile.avatar_public_url = avatar_url
    db.add(user)
    db.add(profile)
    db.commit()

    oauth_account = models.OAuthAccount(
        user_id=user.id,
        provider=provider,
        provider_user_id=provider_user_id,
        provider_email=normalized_email,
    )
    db.add(oauth_account)
    db.commit()
    db.refresh(user)
    return user

from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import auth, models, schemas
from ..config import get_settings
from ..database import get_db
from ..services.auth_tokens import (
    consume_email_verification_token,
    consume_password_reset_token,
    create_email_verification_token,
    create_password_reset_token,
)
from ..services.oauth import (
    build_github_authorize_url,
    build_google_authorize_url,
    exchange_github_code,
    exchange_google_code,
    sanitize_next_path,
    upsert_oauth_user,
)
from ..services.users import ensure_profile, serialize_user

router = APIRouter(tags=["Authentication"])
settings = get_settings()


def serialize_authenticated_user(db: Session, user: models.User) -> schemas.UserResponse:
    refreshed = auth.get_user_by_id(db, user.id)
    return serialize_user(refreshed or user)


@router.post("/register", response_model=schemas.RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = auth.get_user_by_email(db, payload.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered")

    user = models.User(
        name=payload.name.strip(),
        email=payload.email.strip().lower(),
        password_hash=auth.hash_password(payload.password),
        is_verified=False,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered") from exc

    db.refresh(user)
    ensure_profile(db, user)
    verification_token = create_email_verification_token(db, user)

    return schemas.RegisterResponse(
        message="Account created successfully. Verify your email to unlock trusted status.",
        user=serialize_authenticated_user(db, user),
    )


@router.post("/login", response_model=schemas.LoginResponse)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, payload.email.lower(), payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token(subject=str(user.id))
    return schemas.LoginResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=serialize_authenticated_user(db, user),
    )


@router.post("/forgot-password", response_model=schemas.MessageEnvelope)
def forgot_password(payload: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = auth.get_user_by_email(db, payload.email)
    token = create_password_reset_token(db, user) if user else None
    return schemas.MessageEnvelope(
        message="If that email exists, a password reset link has been created.",
        token=token if not settings.is_production else None,
    )


@router.post("/reset-password", response_model=schemas.MessageEnvelope)
def reset_password(payload: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    token = consume_password_reset_token(db, payload.token)
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="That password reset token is invalid or expired.")

    user = auth.get_user_by_id(db, token.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.password_hash = auth.hash_password(payload.new_password)
    db.add(user)
    db.commit()
    return schemas.MessageEnvelope(message="Password updated successfully.")


@router.post("/verify-email/request", response_model=schemas.MessageEnvelope)
def request_email_verification(payload: schemas.RequestEmailVerification, db: Session = Depends(get_db)):
    user = auth.get_user_by_email(db, payload.email)
    token = create_email_verification_token(db, user) if user and not user.is_verified else None
    return schemas.MessageEnvelope(
        message="If the account exists and is unverified, a verification token has been created.",
        token=token if not settings.is_production else None,
    )


@router.post("/verify-email/confirm", response_model=schemas.MessageEnvelope)
def confirm_email_verification(payload: schemas.ConfirmEmailVerification, db: Session = Depends(get_db)):
    token = consume_email_verification_token(db, payload.token)
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="That verification token is invalid or expired.")

    user = auth.get_user_by_id(db, token.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.is_verified = True
    db.add(user)
    db.commit()
    return schemas.MessageEnvelope(message="Email verified successfully.")


@router.get("/oauth/google/start")
def google_oauth_start(next_path: str = Query(default="/dashboard")):
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Google OAuth is not configured.")
    return RedirectResponse(build_google_authorize_url(sanitize_next_path(next_path)), status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/oauth/github/start")
def github_oauth_start(next_path: str = Query(default="/dashboard")):
    if not settings.github_client_id or not settings.github_client_secret:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="GitHub OAuth is not configured.")
    return RedirectResponse(build_github_authorize_url(sanitize_next_path(next_path)), status_code=status.HTTP_307_TEMPORARY_REDIRECT)


def _build_frontend_oauth_redirect(*, next_path: str, token: str | None = None, error: str | None = None) -> RedirectResponse:
    params: dict[str, str] = {"next": next_path}
    if token:
        params["token"] = token
    if error:
        params["error"] = error
    query = urlencode(params)
    return RedirectResponse(
        f"{settings.frontend_origin.rstrip('/')}/oauth/callback?{query}",
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )


async def _complete_oauth_login(*, db: Session, provider: str, code: str, state: str) -> RedirectResponse:
    try:
        state_payload = auth.decode_oauth_state_token(state)
    except ValueError:
        return _build_frontend_oauth_redirect(next_path="/dashboard", error=f"Invalid or expired {provider.title()} sign-in state.")

    next_path = sanitize_next_path(state_payload.get("next"))

    if provider == "google":
        try:
            profile = await exchange_google_code(code)
        except Exception:
            return _build_frontend_oauth_redirect(next_path=next_path, error="Unable to complete Google sign-in.")
        provider_user_id = profile.get("sub")
        email = (profile.get("email") or "").strip().lower()
        if not email or not profile.get("email_verified", False):
            return _build_frontend_oauth_redirect(
                next_path=next_path,
                error="Google account email must be verified before signing in.",
            )
        if not provider_user_id:
            return _build_frontend_oauth_redirect(next_path=next_path, error="Google did not return a valid account identifier.")
        name = profile.get("name") or profile.get("given_name") or email.split("@")[0]
        avatar_url = profile.get("picture")
    else:
        profile = exchange_github_code(code)
        provider_user_id = str(profile.get("id") or "")
        email = (profile.get("email") or "").strip().lower()
        if not email or not provider_user_id:
            return _build_frontend_oauth_redirect(next_path=next_path, error="GitHub did not return a usable email address.")
        name = profile.get("name") or profile.get("login") or email.split("@")[0]
        avatar_url = profile.get("avatar_url")

    user = upsert_oauth_user(
        db,
        provider=provider,
        provider_user_id=provider_user_id,
        email=email,
        name=name,
        avatar_url=avatar_url,
    )
    access_token = auth.create_access_token(subject=str(user.id))
    return _build_frontend_oauth_redirect(next_path=next_path, token=access_token)


@router.get("/oauth/google/callback")
async def google_oauth_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db),
):
    if error:
        return _build_frontend_oauth_redirect(next_path="/dashboard", error="Google sign-in was cancelled or denied.")
    if not code or not state:
        return _build_frontend_oauth_redirect(next_path="/dashboard", error="Missing Google OAuth callback parameters.")
    return await _complete_oauth_login(db=db, provider="google", code=code, state=state)


@router.get("/oauth/github/callback")
async def github_oauth_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db),
):
    if error:
        return _build_frontend_oauth_redirect(next_path="/dashboard", error="GitHub sign-in was cancelled or denied.")
    if not code or not state:
        return _build_frontend_oauth_redirect(next_path="/dashboard", error="Missing GitHub OAuth callback parameters.")
    return await _complete_oauth_login(db=db, provider="github", code=code, state=state)

from __future__ import annotations

import logging
import random
from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect

from .config import get_settings
from .database import Base, engine
from .routes import auth, chat, marketplace, matchmaking, social, users
from .services.rate_limit import request_limit_for

settings = get_settings()
logger = logging.getLogger("skillbarter.api")
# CORSMiddleware matches the incoming `Origin` header exactly.
# We normalize configured origins in backend/config.py to reduce mismatch
# due to whitespace/newlines and trailing slashes.
origins = settings.allowed_origins



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database at startup.

    Must never prevent the ASGI app from loading on Render.
    If Supabase/Postgres is unavailable, we log the error and keep the app running.
    """

    app.state.database_ready = False
    app.state.database_error = None

    try:
        logger.info("Starting database initialization...")

        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())

        required_tables = {
            "users",
            "user_profiles",
            "skills",
            "friend_requests",
            "messages",
            "notifications",
            "learning_requests",
        }

        # Create tables if they do not exist yet.
        if not required_tables.issubset(existing_tables):
            Base.metadata.create_all(bind=engine)

        app.state.database_ready = True
        logger.info("Database startup completed successfully.")

    except Exception as exc:
        # Critical: do not crash startup.
        app.state.database_error = str(exc)
        app.state.database_ready = False
        logger.exception("Database startup failed; continuing without DB-ready state")

    # IMPORTANT: yield control so the application can start.
    yield


# Render/Uvicorn expects an ASGI object named `app`.
app = FastAPI(
    title="SkillBarter API",
    version="1.0.0",
    description="Production-ready authentication backend for the SkillBarter platform.",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(marketplace.router)
app.include_router(matchmaking.router)
app.include_router(social.router)
app.include_router(users.router)


@app.middleware("http")
async def rate_limit_and_log_requests(request: Request, call_next):
    # Best-effort identifier for rate limiting/logging
    identifier = request.headers.get(
        "x-forwarded-for",
        request.client.host if request.client else "unknown",
    )

    # request_limit_for is expected to handle limiting/raising.
    request_limit_for(f"{identifier}:{request.url.path}")

    started = perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Unhandled request error",
            extra={
                "path": request.url.path,
                "method": request.method,
            },
        )
        raise

    duration_ms = round((perf_counter() - started) * 1000, 2)

    if random.random() <= settings.request_log_sample_rate:
        logger.info(
            "request.completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

    response.headers["X-Response-Time-Ms"] = str(duration_ms)
    return response


@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "SkillBarter API",
    }


@app.get("/health", tags=["Health"])
def readiness_check(request: Request):
    return {
        "status": "ok",
        "database": "ready" if getattr(request.app.state, "database_ready", False) else "unavailable",
        "database_error": getattr(request.app.state, "database_error", None),
        "database_url_source": settings.database_url_source,
    }


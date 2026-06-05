from contextlib import asynccontextmanager
import logging
import random
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

from .config import get_settings
from .database import Base, SessionLocal, engine
from .routes import auth, chat, marketplace, matchmaking, social, users
from .services.demo_seed import seed_demo_data
from .services.rate_limit import request_limit_for

settings = get_settings()
logger = logging.getLogger("skillbarter.api")
origins = settings.allowed_origins

@asynccontextmanager
async def lifespan(app: FastAPI):
app.state.database_ready = False
app.state.database_error = None

```
logger.info(
    "database.configuration",
    extra={
        "database_url_source": settings.database_url_source,
        "database_url": settings.database_url_redacted,
    },
)

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

    if not required_tables.issubset(existing_tables):
        logger.info("Creating missing database tables...")
        Base.metadata.create_all(bind=engine)

    # TEMPORARILY DISABLED
    # This is the most likely source of startup hangs/issues.
    #
    # db = SessionLocal()
    # try:
    #     seed_demo_data(db)
    # finally:
    #     db.close()

    app.state.database_ready = True
    logger.info("Database startup completed successfully.")

except Exception as exc:
    app.state.database_error = str(exc)

    logger.exception(
        f"Database startup failed: {exc}",
        extra={
            "database_url_source": settings.database_url_source,
            "database_url": settings.database_url_redacted,
        },
    )

    # Allow FastAPI to start even if DB is unavailable
    app.state.database_ready = False

yield
```

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

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(marketplace.router)
app.include_router(matchmaking.router)
app.include_router(social.router)
app.include_router(users.router)

@app.middleware("http")
async def rate_limit_and_log_requests(request: Request, call_next):
identifier = request.headers.get(
"x-forwarded-for",
request.client.host if request.client else "unknown",
)

```
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
```

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
"database": (
"ready"
if getattr(request.app.state, "database_ready", False)
else "unavailable"
),
"database_error": getattr(request.app.state, "database_error", None),
"database_url_source": settings.database_url_source,
}

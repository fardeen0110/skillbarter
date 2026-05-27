import logging
import random
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routes import auth, chat, marketplace, matchmaking, social, users
from .services.rate_limit import request_limit_for

settings = get_settings()
logger = logging.getLogger("skillbarter.api")
origins = settings.allowed_origins
app = FastAPI(
    title="SkillBarter API",
    version="1.0.0",
    description="Production-ready authentication backend for the SkillBarter platform.",
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
    identifier = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
    request_limit_for(f"{identifier}:{request.url.path}")
    started = perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Unhandled request error", extra={"path": request.url.path, "method": request.method})
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
    return {"status": "ok", "service": "SkillBarter API"}


@app.get("/health", tags=["Health"])
def readiness_check():
    return {"status": "ok"}

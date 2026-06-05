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

        app.state.database_ready = False

    yield

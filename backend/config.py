import os
from pathlib import Path
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


LOCAL_DATABASE_FALLBACK = "postgresql+psycopg://postgres:postgres@localhost:5432/skillbarter"


class Settings(BaseSettings):
    app_env: str = Field(default="development", alias="APP_ENV")
    database_url: str = Field(
        default=LOCAL_DATABASE_FALLBACK,
        alias="DATABASE_URL",
    )
    secret_key: str = Field(default="dev-only-change-me-please", alias="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    frontend_origin: str = Field(default="http://localhost:5173", alias="FRONTEND_ORIGIN")
    cors_origins: str = Field(default="", alias="CORS_ORIGINS")
    google_client_id: str = Field(default="", alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(default="", alias="GOOGLE_CLIENT_SECRET")
    github_client_id: str = Field(default="", alias="GITHUB_CLIENT_ID")
    github_client_secret: str = Field(default="", alias="GITHUB_CLIENT_SECRET")
    oauth_redirect_base_url: str = Field(default="http://localhost:8000", alias="OAUTH_REDIRECT_BASE_URL")
    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_service_role_key: str = Field(default="", alias="SUPABASE_SERVICE_ROLE_KEY")
    supabase_storage_bucket: str = Field(default="skillbarter-assets", alias="SUPABASE_STORAGE_BUCKET")
    rate_limit_requests: int = Field(default=120, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window_seconds: int = Field(default=60, alias="RATE_LIMIT_WINDOW_SECONDS")
    websocket_message_limit: int = Field(default=80, alias="WEBSOCKET_MESSAGE_LIMIT")
    websocket_message_window_seconds: int = Field(default=60, alias="WEBSOCKET_MESSAGE_WINDOW_SECONDS")
    request_log_sample_rate: float = Field(default=1.0, alias="REQUEST_LOG_SAMPLE_RATE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if len(value) < 16:
            raise ValueError("SECRET_KEY must be at least 16 characters long.")
        return value

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("DATABASE_URL is missing.")

        try:
            parsed = make_url(value)
        except ArgumentError as exc:
            raise ValueError("DATABASE_URL is not a valid SQLAlchemy connection string.") from exc

        if not parsed.drivername.startswith("postgresql"):
            raise ValueError("DATABASE_URL must use a PostgreSQL SQLAlchemy dialect.")

        if not parsed.username or not parsed.host:
            raise ValueError("DATABASE_URL must include a username and host.")

        host = parsed.host.lower()
        username = parsed.username

        if host.endswith(".pooler.supabase.com") and not username.startswith("postgres."):
            raise ValueError(
                "Supabase shared pooler URLs on *.pooler.supabase.com must use username format "
                "'postgres.<project-ref>'."
            )

        if host.startswith("db.") and host.endswith(".supabase.co") and username != "postgres":
            raise ValueError(
                "Supabase direct or dedicated pooler URLs on db.<project-ref>.supabase.co must use username "
                "'postgres', not 'postgres.<project-ref>'."
            )

        return value

    @field_validator("access_token_expire_minutes")
    @classmethod
    def validate_expiry(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be positive.")
        return value

    @field_validator("rate_limit_requests", "rate_limit_window_seconds", "websocket_message_limit", "websocket_message_window_seconds")
    @classmethod
    def validate_positive_ints(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Rate limit values must be positive.")
        return value

    @field_validator("request_log_sample_rate")
    @classmethod
    def validate_sample_rate(cls, value: float) -> float:
        if value < 0 or value > 1:
            raise ValueError("REQUEST_LOG_SAMPLE_RATE must be between 0 and 1.")
        return value

    @property
    def allowed_origins(self) -> list[str]:
        """List of allowed CORS origins.

        We normalize inputs to improve matching robustness:
        - split CORS_ORIGINS on commas
        - trim whitespace
        - remove trailing slashes
        - de-duplicate while preserving order
        """

        # FRONTEND_ORIGIN is a single value; it may include whitespace/newlines.
        origins: list[str] = [self.frontend_origin]

        # CORS_ORIGINS is comma-separated (Render env var can sometimes include
        # accidental whitespace/newlines).
        if self.cors_origins:
            origins.extend(
                part.strip()
                for part in self.cors_origins.replace("\n", ",").split(",")
                if part and part.strip()
            )

        normalized: list[str] = []
        for origin in origins:
            cleaned = origin.strip().rstrip("/")
            if cleaned:
                normalized.append(cleaned)

        # Preserve order + de-duplicate
        return list(dict.fromkeys(normalized))


    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def database_url_source(self) -> str:
        if "DATABASE_URL" in os.environ:
            return "process environment variable DATABASE_URL"

        env_file = self.model_config.get("env_file", ".env")
        env_path = Path(env_file) if isinstance(env_file, str) else Path(".env")
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("DATABASE_URL="):
                    return f"{env_path.name} file DATABASE_URL entry"

        return "default fallback in backend/config.py"

    @property
    def database_url_redacted(self) -> str:
        try:
            return make_url(self.database_url).render_as_string(hide_password=True)
        except ArgumentError:
            return "<invalid DATABASE_URL>"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.is_production and settings.secret_key == "dev-only-change-me-please":
        raise ValueError("SECRET_KEY must be explicitly configured in production.")
    if settings.is_production and settings.database_url == LOCAL_DATABASE_FALLBACK:
        raise ValueError(
            "DATABASE_URL is not set in production. Current source is the local fallback in backend/config.py."
        )
    return settings

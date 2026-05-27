from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = Field(default="development", alias="APP_ENV")
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/skillbarter",
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
        origins = [self.frontend_origin]
        origins.extend(
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        )
        return list(dict.fromkeys(origins))

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.is_production and settings.secret_key == "dev-only-change-me-please":
        raise ValueError("SECRET_KEY must be explicitly configured in production.")
    return settings

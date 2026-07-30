from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.environment import Environment


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    app_name: str = "Rigaud Tech Platform ERP"
    app_description: str = "Backend da Rigaud Tech Platform ERP."
    app_env: Environment = Environment.LOCAL
    app_debug: bool | None = None
    app_version: str = "0.1.0"

    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    log_level: str = "INFO"
    application_log_name: str = "application"
    error_log_name: str = "errors"
    audit_log_name: str = "audit"

    database_url: str = Field(
        default="postgresql+psycopg://rigaud:rigaud@localhost:5432/rigaud_erp"
    )
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_timeout: int = 30
    database_pool_recycle: int = 1800
    database_health_timeout_seconds: int = 3

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    jwt_issuer: str | None = None
    jwt_audience: str | None = None

    password_hash_scheme: str = "bcrypt"
    password_min_length: int = 8
    password_max_length: int = 72
    rbac_enabled: bool = True
    mfa_enabled: bool = False
    mfa_encryption_key: str = ""
    mfa_totp_issuer: str = "Rigaud Tech Platform ERP"
    mfa_otp_expire_seconds: int = 300
    mfa_otp_max_attempts: int = 5
    mfa_challenge_expire_seconds: int = 300
    mfa_recovery_codes_count: int = 10
    mfa_rate_limit_attempts: int = 5
    mfa_rate_limit_window_seconds: int = 300
    mfa_required_for_superusers: bool = False
    redis_url: str = "redis://localhost:6379/0"
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    email_otp_dev_enabled: bool = True
    sms_otp_dev_enabled: bool = True

    def validate_security(self) -> None:
        if self.app_env == Environment.PRODUCTION and self.jwt_secret_key in {"", "change-me"}:
            raise RuntimeError("JWT_SECRET_KEY must be configured for production.")
        if self.app_env == Environment.PRODUCTION and not self.mfa_encryption_key:
            raise RuntimeError("MFA_ENCRYPTION_KEY must be configured for production.")

    @property
    def debug_enabled(self) -> bool:
        return self.app_debug if self.app_debug is not None else self.app_env.is_debug

    @property
    def async_database_url(self) -> str:
        if self.database_url.startswith("postgresql+psycopg://"):
            return self.database_url.replace(
                "postgresql+psycopg://",
                "postgresql+psycopg_async://",
                1,
            )
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

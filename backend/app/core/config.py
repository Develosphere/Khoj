from pathlib import Path

from pydantic import Field, ValidationError, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from backend/.env via pydantic-settings.

    Fields are required and validated to be non-empty strings to avoid
    silent misconfiguration when values are missing.
    """

    SUPABASE_URL: str = Field(..., min_length=1, description="Supabase project URL")
    SUPABASE_ANON_KEY: str = Field(..., min_length=1, description="Supabase anon key")
    BACKEND_CORS_ORIGINS: str = Field(
        ...,
        min_length=1,
        description="Comma-separated list of allowed frontend origins for CORS",
    )

    @field_validator("BACKEND_CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, value: str) -> str:
        origins = [origin.strip() for origin in value.split(",") if origin.strip()]
        if not origins:
            raise ValueError("BACKEND_CORS_ORIGINS must include at least one allowed origin")
        return value

    @computed_field
    @property
    def backend_cors_origins(self) -> list[str]:
        """Parsed CORS origins for FastAPI middleware."""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        validate_assignment=True,
        extra="ignore",
    )


try:
    settings = Settings()
except ValidationError as e:
    # Build a descriptive error message for missing/invalid configuration
    msgs = "; ".join([
        f"{'.'.join(map(str, err.get('loc', [])))}: {err.get('msg')}" for err in e.errors()
    ])
    raise RuntimeError(f"Configuration validation error: {msgs}") from e

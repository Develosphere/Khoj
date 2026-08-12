from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from backend/.env via pydantic-settings.

    Fields are required and validated to be non-empty strings to avoid
    silent misconfiguration when values are missing.
    """

    SUPABASE_URL: str = Field(..., min_length=1, description="Supabase project URL")
    SUPABASE_ANON_KEY: str = Field(..., min_length=1, description="Supabase anon key")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        validate_assignment=True,
        extra="forbid",
    )


try:
    settings = Settings()
except ValidationError as e:
    # Build a descriptive error message for missing/invalid configuration
    msgs = "; ".join([
        f"{'.'.join(map(str, err.get('loc', [])))}: {err.get('msg')}" for err in e.errors()
    ])
    raise RuntimeError(f"Configuration validation error: {msgs}") from e

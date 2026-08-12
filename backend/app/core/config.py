from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env."""

    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    BACKEND_CORS_METHODS: list[str] = ["GET", "POST", "OPTIONS", "PUT", "DELETE"]
    BACKEND_CORS_HEADERS: list[str] = ["Authorization", "Content-Type"]

    @property
    def CORS_ALLOWED_ORIGINS(self) -> list[str]:
        return self.BACKEND_CORS_ORIGINS

    @property
    def CORS_ALLOWED_METHODS(self) -> list[str]:
        return self.BACKEND_CORS_METHODS

    @property
    def CORS_ALLOWED_HEADERS(self) -> list[str]:
        return self.BACKEND_CORS_HEADERS

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

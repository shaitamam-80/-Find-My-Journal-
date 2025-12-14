"""
Application configuration using pydantic-settings.
Loads environment variables from .env file.
"""
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# Find the project root (where .env is located)
def find_env_file() -> Path:
    """Find the .env file in project root or current directory."""
    current = Path(__file__).resolve()
    # Go up until we find .env or reach root
    for parent in [current] + list(current.parents):
        env_path = parent / ".env"
        if env_path.exists():
            return env_path
    # Fallback to current directory
    return Path(".env")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Supabase
    supabase_url: str
    supabase_key: str  # Can be anon key or service_role key
    supabase_service_role_key: str = ""  # Service role key for bypassing RLS

    # OpenAlex
    openalex_email: str = ""
    openalex_api_key: str = ""

    # App settings
    app_name: str = "Find My Journal API"
    app_version: str = "1.0.0"
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=str(find_env_file()),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to avoid reading .env file on every call.
    """
    return Settings()

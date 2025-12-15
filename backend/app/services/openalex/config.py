"""
OpenAlex Service Configuration

Sets up pyalex library with email and API key for polite pool.
"""
import pyalex
from functools import lru_cache
from typing import Optional

from app.core.config import get_settings as get_app_settings


class OpenAlexConfig:
    """OpenAlex-specific configuration."""

    # Default values
    MAX_RESULTS: int = 25
    MIN_JOURNAL_WORKS: int = 500
    WORKS_PER_PAGE: int = 200
    MAX_SEARCH_TERMS: int = 10

    def __init__(self):
        self._configure_pyalex()

    def _configure_pyalex(self) -> None:
        """Configure pyalex with credentials from app settings."""
        settings = get_app_settings()
        if settings.openalex_email:
            pyalex.config.email = settings.openalex_email
        if settings.openalex_api_key:
            pyalex.config.api_key = settings.openalex_api_key


@lru_cache
def get_config() -> OpenAlexConfig:
    """Get cached OpenAlex configuration."""
    return OpenAlexConfig()


def get_max_results() -> int:
    """Get maximum results per search."""
    return get_config().MAX_RESULTS


def get_min_journal_works() -> int:
    """Get minimum works count for journal inclusion."""
    return get_config().MIN_JOURNAL_WORKS

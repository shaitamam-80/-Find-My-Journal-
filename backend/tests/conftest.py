"""
Root conftest.py - Shared pytest fixtures for all backend tests.

This file provides common fixtures for:
- Async test support
- Database mocking
- Authentication mocking
- API client setup
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from typing import Generator, Dict, Any
from datetime import date

# Import FastAPI test client
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def anyio_backend():
    """Configure anyio to use asyncio for async tests."""
    return "asyncio"


@pytest.fixture
def mock_settings():
    """Mock application settings."""
    with patch("app.core.config.get_settings") as mock:
        mock.return_value = MagicMock(
            supabase_url="https://test.supabase.co",
            supabase_key="test-key",
            supabase_service_role_key="test-service-key",
            openalex_email="test@test.com",
            openalex_api_key="",
            nlm_api_key="",
            trust_safety_enabled=False,
            gemini_api_key="",
            gemini_explanation_enabled=False,
            app_name="Test App",
            app_version="1.0.0",
            debug=True,
            log_level="DEBUG",
            free_user_daily_limit=2,
            free_user_explanation_limit=15,
        )
        yield mock


@pytest.fixture
def mock_db_service():
    """Mock database service for isolated tests."""
    with patch("app.services.db_service.db_service") as mock:
        mock.check_connection.return_value = True
        mock.get_profile_by_id.return_value = {
            "id": "test-user-id",
            "email": "test@example.com",
            "tier": "free",
            "credits_used_today": 0,
            "last_search_date": None,
            "explanations_used_today": 0,
            "last_explanation_date": None,
        }
        mock.log_search = AsyncMock(return_value=True)
        mock.save_search = AsyncMock(return_value="search-id")
        mock.get_saved_searches = AsyncMock(return_value=[])
        mock.submit_feedback = AsyncMock(return_value="feedback-id")
        yield mock


@pytest.fixture
def mock_user_profile() -> Dict[str, Any]:
    """Sample user profile data."""
    return {
        "id": "test-user-uuid",
        "email": "researcher@university.edu",
        "tier": "free",
        "credits_used_today": 0,
        "last_search_date": str(date.today()),
        "explanations_used_today": 0,
        "last_explanation_date": None,
    }


@pytest.fixture
def mock_paid_user_profile() -> Dict[str, Any]:
    """Sample paid user profile data."""
    return {
        "id": "paid-user-uuid",
        "email": "premium@university.edu",
        "tier": "paid",
        "credits_used_today": 100,
        "last_search_date": str(date.today()),
        "explanations_used_today": 50,
        "last_explanation_date": str(date.today()),
    }


@pytest.fixture
def mock_jwt_token() -> str:
    """Mock JWT token for authentication tests."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItdXVpZCIsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsImV4cCI6OTk5OTk5OTk5OX0.test"


@pytest.fixture
def auth_headers(mock_jwt_token: str) -> Dict[str, str]:
    """Authorization headers with mock JWT token."""
    return {"Authorization": f"Bearer {mock_jwt_token}"}


@pytest.fixture
def sample_search_request() -> Dict[str, Any]:
    """Sample search request payload."""
    return {
        "title": "Machine Learning for Medical Image Analysis",
        "abstract": "This study explores the application of deep learning neural networks for automated diagnosis of medical images. We compare convolutional neural network architectures for classification tasks.",
        "keywords": ["machine learning", "medical imaging", "deep learning"],
        "prefer_open_access": False,
        "incognito_mode": False,
    }


@pytest.fixture
def sample_psychology_search_request() -> Dict[str, Any]:
    """Sample psychology search request for testing discipline detection."""
    return {
        "title": "Development of Empathy in Young Children",
        "abstract": "This longitudinal study examines the emotional development of empathy and prosocial behavior in toddlers aged 18-36 months. We investigate the role of attachment and parenting styles.",
        "keywords": ["child development", "empathy", "prosocial behavior"],
        "prefer_open_access": True,
        "incognito_mode": False,
    }


@pytest.fixture
def app_client(mock_settings, mock_db_service) -> Generator[TestClient, None, None]:
    """Create test client with mocked dependencies."""
    from app.main import app

    with TestClient(app) as client:
        yield client


# Re-export fixtures from openalex conftest for convenience
pytest_plugins = ["tests.services.openalex.conftest"]

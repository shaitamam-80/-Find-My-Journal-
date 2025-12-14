"""
Tests for authentication and rate limiting.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from fastapi.testclient import TestClient

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.models.user import UserProfile, UserTier

client = TestClient(app)


class TestAuthEndpointsWithoutToken:
    """Test auth endpoints without authentication."""

    def test_me_without_token_returns_401(self):
        """Accessing /me without token should return 401."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_limits_without_token_returns_401(self):
        """Accessing /limits without token should return 401."""
        response = client.get("/api/v1/auth/limits")
        assert response.status_code == 401

    def test_test_search_without_token_returns_401(self):
        """Accessing /test-search without token should return 401."""
        response = client.post("/api/v1/auth/test-search")
        assert response.status_code == 401

    def test_admin_only_without_token_returns_401(self):
        """Accessing /admin-only without token should return 401."""
        response = client.get("/api/v1/auth/admin-only")
        assert response.status_code == 401


class TestUserProfileModel:
    """Test UserProfile model logic."""

    def test_free_user_can_search_first_time(self):
        """Free user should be able to search if no searches today."""
        user = UserProfile(
            id="test-id",
            tier=UserTier.FREE,
            credits_used_today=0,
            last_search_date=None
        )
        assert user.can_search(daily_limit=2) is True

    def test_free_user_can_search_under_limit(self):
        """Free user should be able to search if under limit."""
        user = UserProfile(
            id="test-id",
            tier=UserTier.FREE,
            credits_used_today=1,
            last_search_date=date.today()
        )
        assert user.can_search(daily_limit=2) is True

    def test_free_user_cannot_search_at_limit(self):
        """Free user should NOT be able to search if at limit."""
        user = UserProfile(
            id="test-id",
            tier=UserTier.FREE,
            credits_used_today=2,
            last_search_date=date.today()
        )
        assert user.can_search(daily_limit=2) is False

    def test_free_user_cannot_search_over_limit(self):
        """Free user should NOT be able to search if over limit."""
        user = UserProfile(
            id="test-id",
            tier=UserTier.FREE,
            credits_used_today=5,
            last_search_date=date.today()
        )
        assert user.can_search(daily_limit=2) is False

    def test_free_user_can_search_new_day(self):
        """Free user should be able to search on new day even if was at limit."""
        user = UserProfile(
            id="test-id",
            tier=UserTier.FREE,
            credits_used_today=5,
            last_search_date=date(2020, 1, 1)  # Old date
        )
        assert user.can_search(daily_limit=2) is True

    def test_paid_user_has_unlimited_searches(self):
        """Paid user should have unlimited searches."""
        user = UserProfile(
            id="test-id",
            tier=UserTier.PAID,
            credits_used_today=100,
            last_search_date=date.today()
        )
        assert user.has_unlimited_searches is True
        assert user.can_search(daily_limit=2) is True

    def test_admin_has_unlimited_searches(self):
        """Admin should have unlimited searches."""
        user = UserProfile(
            id="test-id",
            tier=UserTier.SUPER_ADMIN,
            credits_used_today=100,
            last_search_date=date.today()
        )
        assert user.has_unlimited_searches is True
        assert user.can_search(daily_limit=2) is True

    def test_admin_is_admin(self):
        """Admin user should be recognized as admin."""
        user = UserProfile(
            id="test-id",
            tier=UserTier.SUPER_ADMIN,
        )
        assert user.is_admin is True

    def test_paid_user_is_not_admin(self):
        """Paid user should NOT be admin."""
        user = UserProfile(
            id="test-id",
            tier=UserTier.PAID,
        )
        assert user.is_admin is False

    def test_free_user_is_not_admin(self):
        """Free user should NOT be admin."""
        user = UserProfile(
            id="test-id",
            tier=UserTier.FREE,
        )
        assert user.is_admin is False


class TestRateLimitLogic:
    """Test rate limiting constants and logic."""

    def test_daily_limit_is_two(self):
        """Daily limit for free users should be 2."""
        from app.core.security import FREE_USER_DAILY_LIMIT
        assert FREE_USER_DAILY_LIMIT == 2


class TestEndpointWithMockedAuth:
    """Test endpoints with mocked authentication."""

    @patch("app.api.v1.auth.get_current_user")
    def test_me_returns_user_info(self, mock_get_user):
        """Test /me returns correct user info."""
        mock_user = UserProfile(
            id="test-123",
            email="test@example.com",
            tier=UserTier.FREE,
            credits_used_today=1,
            last_search_date=date.today()
        )
        mock_get_user.return_value = mock_user

        # Note: Mocking doesn't work with TestClient dependencies easily
        # This is more of a placeholder for integration tests
        # Real tests would use actual Supabase tokens
        pass


class TestOpenAPISchema:
    """Test that OpenAPI schema includes auth endpoints."""

    def test_openapi_includes_auth_endpoints(self):
        """OpenAPI schema should include auth endpoints."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        paths = schema.get("paths", {})

        assert "/api/v1/auth/me" in paths
        assert "/api/v1/auth/limits" in paths
        assert "/api/v1/auth/test-search" in paths
        assert "/api/v1/auth/admin-only" in paths

"""
Health endpoint tests.

Tests the /health endpoint for basic API functionality.
"""
import pytest
from unittest.mock import patch, MagicMock


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_endpoint_db_connected(self, app_client):
        """Test health endpoint returns ok when DB is connected."""
        response = app_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["db"] == "connected"

    def test_health_endpoint_db_disconnected(self, app_client):
        """Test health endpoint returns degraded when DB is disconnected."""
        with patch("app.main.db_service") as mock_db:
            mock_db.check_connection.return_value = False

            response = app_client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["db"] == "disconnected"


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_endpoint(self, app_client):
        """Test root endpoint returns API info."""
        response = app_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["docs"] == "/docs"

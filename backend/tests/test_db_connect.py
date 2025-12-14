"""
Tests for database connection and health endpoint.
"""
import pytest
from fastapi.testclient import TestClient

import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.services.db_service import DBService


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_endpoint_returns_200(self):
        """Health endpoint should return 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_has_status(self):
        """Health endpoint should include status field."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] in ["ok", "degraded"]

    def test_health_endpoint_has_db_status(self):
        """Health endpoint should include db field."""
        response = client.get("/health")
        data = response.json()
        assert "db" in data
        assert data["db"] in ["connected", "disconnected"]


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_returns_200(self):
        """Root endpoint should return 200 OK."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_has_app_info(self):
        """Root endpoint should return app information."""
        response = client.get("/")
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data


class TestDBService:
    """Tests for the DBService class."""

    def test_db_service_singleton(self):
        """DBService should be a singleton."""
        service1 = DBService()
        service2 = DBService()
        assert service1 is service2

    def test_db_service_has_client(self):
        """DBService should have a client property."""
        service = DBService()
        assert service.client is not None

    def test_check_connection(self):
        """check_connection should return a boolean."""
        service = DBService()
        result = service.check_connection()
        assert isinstance(result, bool)


class TestDatabaseConnection:
    """Integration tests for actual database connection."""

    def test_supabase_connection_works(self):
        """Should successfully connect to Supabase."""
        service = DBService()
        connected = service.check_connection()
        assert connected is True, "Failed to connect to Supabase. Check your .env file."

    def test_health_shows_connected(self):
        """Health endpoint should show db as connected."""
        response = client.get("/health")
        data = response.json()
        assert data["db"] == "connected", "Database should be connected"
        assert data["status"] == "ok", "Status should be ok when db is connected"

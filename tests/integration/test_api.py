"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.api import app
from src.config import settings


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def api_key():
    """Get valid API key for testing."""
    # Mock the settings to use a test API key
    with patch.object(settings, "api_keys", "test-api-key"):
        with patch.object(settings, "get_api_keys_list", return_value=["test-api-key"]):
            yield "test-api-key"


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()
    assert "version" in response.json()


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "database" in data


def test_get_books_without_api_key(client):
    """Test getting books without API key."""
    response = client.get("/api/v1/books")
    assert response.status_code == 401


def test_get_books_with_invalid_api_key(client):
    """Test getting books with invalid API key."""
    response = client.get(
        "/api/v1/books", headers={settings.api_key_header: "invalid-key"}
    )
    assert response.status_code == 401


@patch("src.database.db_client.get_books")
@patch("src.database.db_client.collection")
def test_get_books_with_valid_api_key(mock_collection, mock_get_books, client, api_key):
    """Test getting books with valid API key."""
    # Mock database response
    mock_get_books.return_value = []
    mock_collection.count_documents.return_value = 0

    response = client.get(
        "/api/v1/books", headers={settings.api_key_header: api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert "books" in data
    assert "total" in data


@patch("src.database.db_client.get_stats")
def test_get_stats(mock_get_stats, client, api_key):
    """Test getting statistics."""
    from src.database.models import CrawlStats

    mock_stats = CrawlStats(
        total_books=100, total_categories=10, total_pages=50
    )
    mock_get_stats.return_value = mock_stats

    response = client.get(
        "/api/v1/books/stats", headers={settings.api_key_header: api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_books"] == 100
    assert data["total_categories"] == 10

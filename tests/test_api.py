"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


class TestBooksAPI:
    """Test /books endpoints with authentication."""

    def test_get_books_unauthorized(self, client: TestClient) -> None:
        """Test missing API key."""
        response = client.get("/api/v1/books")
        assert response.status_code == 401

    def test_get_books_invalid_key(self, client: TestClient) -> None:
        """Test invalid API key."""
        response = client.get("/api/v1/books", headers={"X-API-Key": "invalid-key"})
        assert response.status_code == 403

    def test_get_books_invalid_sort(self, client: TestClient) -> None:
        """Test invalid sort parameter."""
        response = client.get(
            "/api/v1/books?sort_by=invalid",
            headers={"X-API-Key": "test-key-123"},
        )
        assert response.status_code == 422

    def test_get_books_invalid_rating(self, client: TestClient) -> None:
        """Test invalid rating filter."""
        response = client.get(
            "/api/v1/books?rating=10",  # Rating must be 0-5
            headers={"X-API-Key": "test-key-123"},
        )
        assert response.status_code == 422

    def test_get_books_invalid_limit(self, client: TestClient) -> None:
        """Test invalid limit (>100)."""
        response = client.get(
            "/api/v1/books?limit=101",
            headers={"X-API-Key": "test-key-123"},
        )
        assert response.status_code == 422


class TestChangesAPI:
    """Test /changes endpoint with authentication."""

    def test_get_changes_unauthorized(self, client: TestClient) -> None:
        """Test missing API key."""
        response = client.get("/api/v1/changes")
        assert response.status_code == 401

    def test_get_changes_invalid_key(self, client: TestClient) -> None:
        """Test invalid API key."""
        response = client.get("/api/v1/changes", headers={"X-API-Key": "invalid-key"})
        assert response.status_code == 403

    def test_get_changes_invalid_hours(self, client: TestClient) -> None:
        """Test invalid hours parameter."""
        response = client.get(
            "/api/v1/changes?hours=1000",  # Max 720
            headers={"X-API-Key": "test-key-123"},
        )
        assert response.status_code == 422

    def test_get_changes_invalid_limit(self, client: TestClient) -> None:
        """Test invalid limit (>100)."""
        response = client.get(
            "/api/v1/changes?limit=101",
            headers={"X-API-Key": "test-key-123"},
        )
        assert response.status_code == 422


class TestRateLimiting:
    """Test rate limiting middleware."""

    def test_rate_limit_headers(self, client: TestClient) -> None:
        """Test rate limiting headers are present."""
        response = client.get("/api/v1/books", headers={"X-API-Key": "test-key-123"})
        # May fail due to missing DB, but headers should be present
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers


class TestBooksAPI:
    """Test /books endpoints."""

    def test_get_books_unauthorized(self, client: TestClient) -> None:
        """Test missing API key."""
        response = client.get("/api/v1/books")
        assert response.status_code == 401
        assert "X-API-Key" in response.json()["detail"]

    def test_get_books_invalid_key(self, client: TestClient) -> None:
        """Test invalid API key."""
        response = client.get("/api/v1/books", headers={"X-API-Key": "invalid-key"})
        assert response.status_code == 403

    def test_get_books_valid_key_empty(self, client: TestClient) -> None:
        """Test GET /books with valid API key but no data."""
        response = client.get("/api/v1/books", headers={"X-API-Key": "test-key-123"})
        # Should return 200 with empty list
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_books_pagination(self, client: TestClient) -> None:
        """Test pagination parameters."""
        response = client.get("/api/v1/books?page=1&limit=5", headers={"X-API-Key": "test-key-123"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_get_books_sorting_options(self, client: TestClient) -> None:
        """Test different sort options."""
        sort_options = ["name", "price", "rating", "reviews"]
        for sort in sort_options:
            response = client.get(
                f"/api/v1/books?sort_by={sort}", headers={"X-API-Key": "test-key-123"}
            )
            assert response.status_code == 200

    def test_get_books_invalid_sort(self, client: TestClient) -> None:
        """Test invalid sort parameter."""
        response = client.get(
            "/api/v1/books?sort_by=invalid", headers={"X-API-Key": "test-key-123"}
        )
        assert response.status_code == 422  # Validation error

    def test_get_books_price_filter(self, client: TestClient) -> None:
        """Test price range filter."""
        response = client.get(
            "/api/v1/books?min_price=10&max_price=50", headers={"X-API-Key": "test-key-123"}
        )
        assert response.status_code == 200

    def test_get_books_rating_filter(self, client: TestClient) -> None:
        """Test rating filter."""
        response = client.get("/api/v1/books?rating=4.0", headers={"X-API-Key": "test-key-123"})
        assert response.status_code == 200

    def test_get_books_category_filter(self, client: TestClient) -> None:
        """Test category filter."""
        response = client.get(
            "/api/v1/books?category=Fiction", headers={"X-API-Key": "test-key-123"}
        )
        assert response.status_code == 200


class TestChangesAPI:
    """Test /changes endpoint."""

    def test_get_changes_unauthorized(self, client: TestClient) -> None:
        """Test missing API key on /changes."""
        response = client.get("/api/v1/changes")
        assert response.status_code == 401

    def test_get_changes_valid_key(self, client: TestClient) -> None:
        """Test GET /changes with valid key."""
        response = client.get("/api/v1/changes", headers={"X-API-Key": "test-key-123"})
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_changes_hours_filter(self, client: TestClient) -> None:
        """Test hours parameter."""
        response = client.get("/api/v1/changes?hours=48", headers={"X-API-Key": "test-key-123"})
        assert response.status_code == 200

    def test_get_changes_pagination(self, client: TestClient) -> None:
        """Test pagination on changes."""
        response = client.get(
            "/api/v1/changes?page=1&limit=5", headers={"X-API-Key": "test-key-123"}
        )
        assert response.status_code == 200
        assert len(response.json()) <= 5


class TestRateLimiting:
    """Test rate limiting middleware."""

    def test_rate_limit_headers(self, client: TestClient) -> None:
        """Test rate limit headers present in response."""
        response = client.get("/api/v1/books", headers={"X-API-Key": "test-key-123"})
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers

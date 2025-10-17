"""Unit tests for configuration."""

import pytest
from pydantic import ValidationError

from src.config import Settings


def test_settings_default_values():
    """Test settings with default values."""
    settings = Settings(api_keys="test-key")

    assert settings.mongodb_url == "mongodb://localhost:27017"
    assert settings.mongodb_db_name == "books_crawler"
    assert settings.crawler_max_concurrent_requests == 10
    assert settings.api_port == 8000


def test_settings_custom_values():
    """Test settings with custom values."""
    settings = Settings(
        mongodb_url="mongodb://custom:27017",
        crawler_max_concurrent_requests=5,
        api_keys="key1,key2",
    )

    assert settings.mongodb_url == "mongodb://custom:27017"
    assert settings.crawler_max_concurrent_requests == 5
    assert settings.get_api_keys_list() == ["key1", "key2"]


def test_settings_validation():
    """Test settings validation."""
    # Test invalid port
    with pytest.raises(ValidationError):
        Settings(api_port=99999, api_keys="test")

    # Test invalid concurrent requests
    with pytest.raises(ValidationError):
        Settings(crawler_max_concurrent_requests=200, api_keys="test")


def test_api_keys_list():
    """Test API keys list parsing."""
    settings = Settings(api_keys="key1, key2 , key3")
    keys = settings.get_api_keys_list()

    assert len(keys) == 3
    assert "key1" in keys
    assert "key2" in keys
    assert "key3" in keys


def test_api_keys_validation():
    """Test API keys validation."""
    with pytest.raises(ValidationError):
        Settings(api_keys="")

    with pytest.raises(ValidationError):
        Settings(api_keys="   ")

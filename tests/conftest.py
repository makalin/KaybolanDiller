import pytest
from fastapi.testclient import TestClient
from api.main import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)

@pytest.fixture
def sample_text():
    """Sample text for testing"""
    return "Hello world"

@pytest.fixture
def valid_language_pair():
    """Valid language pair for testing"""
    return {
        "source_lang": "en",
        "target_lang": "tr"
    }

@pytest.fixture
def invalid_language_pair():
    """Invalid language pair for testing"""
    return {
        "source_lang": "invalid",
        "target_lang": "tr"
    } 
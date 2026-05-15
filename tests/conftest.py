import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("USE_MOCK_TRANSLATION", "true")

from api.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_text():
    return "Hello world"


@pytest.fixture
def valid_language_pair():
    return {"source_language": "en", "target_language": "tr"}


@pytest.fixture
def invalid_language_pair():
    return {"source_language": "invalid", "target_language": "tr"}

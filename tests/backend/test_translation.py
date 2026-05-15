import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("USE_MOCK_TRANSLATION", "true")

from api.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "mock_mode" in data


def test_list_languages():
    response = client.get("/api/languages")
    assert response.status_code == 200
    data = response.json()
    assert "languages" in data
    assert data["total"] >= 10
    assert any(lang["code"] == "tr" for lang in data["languages"])


def test_translate_endpoint():
    response = client.post(
        "/api/translate",
        json={
            "source_text": "Hello",
            "source_language": "en",
            "target_language": "tr",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "translated_text" in body
    assert body["source_language"] == "en"
    assert body["target_language"] == "tr"
    assert body["confidence_score"] > 0


def test_translate_legacy_fields():
    response = client.post(
        "/api/translate",
        json={
            "text": "hello",
            "source_lang": "en",
            "target_lang": "mes",
        },
    )
    assert response.status_code == 200
    assert response.json()["translated_text"]


def test_language_detection():
    response = client.post(
        "/api/detect",
        json={"text": "Merhaba dünya"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "detected_language" in body
    assert body["confidence"] > 0


def test_invalid_language_pair():
    response = client.post(
        "/api/translate",
        json={
            "source_text": "Hello",
            "source_language": "invalid",
            "target_language": "tr",
        },
    )
    assert response.status_code == 400


def test_empty_text():
    response = client.post(
        "/api/translate",
        json={
            "source_text": "",
            "source_language": "en",
            "target_language": "tr",
        },
    )
    assert response.status_code in (400, 422)


def test_models_endpoint():
    response = client.get("/api/models/en/tr")
    assert response.status_code == 200
    data = response.json()
    assert data["source_language"] == "en"
    assert len(data["models"]) >= 1


def test_batch_translate():
    response = client.post(
        "/api/translate/batch",
        json={
            "texts": ["Hello", "Thank you"],
            "source_language": "en",
            "target_language": "mes",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert len(data["translations"]) == 2


def test_demo_lexicon():
    response = client.post(
        "/api/translate",
        json={
            "source_text": "hello",
            "source_language": "en",
            "target_language": "mes",
        },
    )
    assert response.status_code == 200
    assert response.json()["translated_text"] == "salam"


def test_same_language_rejected():
    response = client.post(
        "/api/translate",
        json={
            "source_text": "test",
            "source_language": "en",
            "target_language": "en",
        },
    )
    assert response.status_code == 400

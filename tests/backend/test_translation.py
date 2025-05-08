import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_translate_endpoint():
    """Test the basic translation endpoint"""
    response = client.post(
        "/api/translate",
        json={
            "source_text": "Hello",
            "source_lang": "en",
            "target_lang": "tr"
        }
    )
    assert response.status_code == 200
    assert "translated_text" in response.json()

def test_language_detection():
    """Test the language detection endpoint"""
    response = client.post(
        "/api/detect",
        json={
            "text": "Merhaba dünya"
        }
    )
    assert response.status_code == 200
    assert "detected_language" in response.json()

def test_invalid_language_pair():
    """Test translation with invalid language pair"""
    response = client.post(
        "/api/translate",
        json={
            "source_text": "Hello",
            "source_lang": "invalid",
            "target_lang": "tr"
        }
    )
    assert response.status_code == 400

def test_empty_text():
    """Test translation with empty text"""
    response = client.post(
        "/api/translate",
        json={
            "source_text": "",
            "source_lang": "en",
            "target_lang": "tr"
        }
    )
    assert response.status_code == 400 
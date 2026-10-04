import os

import pytest

from src.core.config import MODEL_PATH


def test_health_endpoints(client):
    assert client.get("/health").json() == {"status": "healthy"}
    assert client.get("/api/health").json() == {"status": "healthy"}


def test_predict_returns_expected_schema(client, valid_payload):
    r = client.post("/api/predict", json=valid_payload)
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body["recommended_crop"], str) and body["recommended_crop"]
    assert 0 <= body["confidence"] <= 100
    assert len(body["top_crops"]) >= 1
    assert body["irrigation_technique"]


@pytest.mark.skipif(not os.path.exists(MODEL_PATH), reason="model not trained; run `make train`")
def test_predict_known_rice_profile(client, valid_payload):
    """The classic rice sample should be recognised as rice (needs trained model)."""
    body = client.post("/api/predict", json=valid_payload).json()
    assert body["recommended_crop"] == "rice"


def test_predict_is_deterministic(client, valid_payload):
    a = client.post("/api/predict", json=valid_payload).json()
    b = client.post("/api/predict", json=valid_payload).json()
    assert a == b


def test_missing_field_is_rejected(client, valid_payload):
    del valid_payload["ph"]
    assert client.post("/api/predict", json=valid_payload).status_code == 422


def test_wrong_type_is_rejected(client, valid_payload):
    valid_payload["rainfall"] = "lots"
    assert client.post("/api/predict", json=valid_payload).status_code == 422


@pytest.mark.parametrize("field,value", [("humidity", 182), ("ph", 60), ("rainfall", -5)])
def test_out_of_range_values_are_rejected(client, valid_payload, field, value):
    valid_payload[field] = value
    assert client.post("/api/predict", json=valid_payload).status_code == 422


def test_water_saved_is_reported_per_hectare(client, valid_payload):
    one = client.post("/api/predict", json={**valid_payload, "field_size_hectares": 1}).json()
    five = client.post("/api/predict", json={**valid_payload, "field_size_hectares": 5}).json()
    assert one["water_saved_liters_ha"] == five["water_saved_liters_ha"]


def test_chat_without_api_key_degrades_gracefully(client, monkeypatch):
    monkeypatch.setattr("src.api.endpoints.GROQ_API_KEY", None)
    r = client.post("/api/chat", json={"message": "hi", "farm_context": {}})
    assert r.status_code == 200
    assert "reply" in r.json()


def test_fallback_when_model_missing(client, valid_payload, monkeypatch):
    """With no trained model the API must still answer using the rule-based fallback."""
    import src.ml.predict as predict
    monkeypatch.setattr(predict, "_model_cache", None)
    monkeypatch.setattr(predict, "MODEL_PATH", "/nonexistent/model.joblib")
    r = client.post("/api/predict", json=valid_payload)
    assert r.status_code == 200
    assert r.json()["recommended_crop"] == "rice"  # rainfall 203 > 200

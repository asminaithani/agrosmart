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


@pytest.mark.skipif(not os.path.exists(MODEL_PATH), reason="model not trained; run `make train`")
@pytest.mark.parametrize("name", ["rice", "cotton", "mango", "maize"])
def test_ui_presets_predict_their_own_crop(client, name):
    """Every preset button in the UI must be a crop the model can actually recognise."""
    from src.frontend.mock_data import PRESETS
    body = client.post("/api/predict", json=PRESETS[name]).json()
    assert body["recommended_crop"] == name


def test_unhandled_error_returns_clean_json_500(valid_payload, tmp_path, monkeypatch):
    """An unexpected exception must not leak a stack trace to the client."""
    from fastapi.testclient import TestClient
    import src.api.endpoints as endpoints
    from src.api.main import app

    monkeypatch.setenv("AGROSMART_DB_PATH", str(tmp_path / "t.db"))

    async def boom(_):
        raise RuntimeError("simulated failure")

    monkeypatch.setattr(endpoints, "run_pipeline", boom)
    r = TestClient(app, raise_server_exceptions=False).post("/api/predict", json=valid_payload)
    assert r.status_code == 500
    assert r.json() == {"error": "Internal server error"}


def test_requests_are_logged(client, valid_payload, caplog):
    import logging
    with caplog.at_level(logging.INFO):
        client.post("/api/predict", json=valid_payload)
    messages = " ".join(rec.getMessage() for rec in caplog.records)
    assert "POST /api/predict -> 200" in messages
    assert "Prediction: crop=" in messages

from src.db import database as db

SAMPLE = {"N": 90, "P": 42, "K": 43, "temperature": 21.0, "humidity": 82.0,
          "ph": 6.5, "rainfall": 203.0, "field_size_hectares": 2.0}


def test_log_and_read_back(tmp_path, monkeypatch):
    monkeypatch.setenv("AGROSMART_DB_PATH", str(tmp_path / "t.db"))
    row_id = db.log_prediction(SAMPLE, "rice", 97.0, "Drip Irrigation")
    rows = db.recent_predictions()
    assert rows[0]["id"] == row_id
    assert rows[0]["predicted_crop"] == "rice"
    assert rows[0]["field_size_ha"] == 2.0


def test_stats_group_by_crop(tmp_path, monkeypatch):
    monkeypatch.setenv("AGROSMART_DB_PATH", str(tmp_path / "t.db"))
    db.log_prediction(SAMPLE, "rice", 90.0, "Drip Irrigation")
    db.log_prediction(SAMPLE, "rice", 100.0, "Drip Irrigation")
    db.log_prediction({**SAMPLE, "rainfall": 60.0}, "wheat", 80.0, "Optimized Flood Irrigation")
    stats = db.prediction_stats()
    assert stats["total_predictions"] == 3
    assert stats["by_crop"][0]["crop"] == "rice"
    assert stats["by_crop"][0]["count"] == 2
    assert stats["by_crop"][0]["avg_confidence_pct"] == 95.0


def test_prediction_endpoint_logs_to_database(client, valid_payload):
    client.post("/api/predict", json=valid_payload)
    client.post("/api/predict", json=valid_payload)
    stats = client.get("/api/stats").json()
    assert stats["total_predictions"] == 2
    assert len(client.get("/api/history").json()) == 2

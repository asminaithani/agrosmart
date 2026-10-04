"""SQLite persistence for prediction history.

Uses only the standard library. The database path can be overridden with the
AGROSMART_DB_PATH environment variable (the tests point it at a temp file).
"""
import os
import sqlite3
from typing import Any, Dict, List

from src.core.config import BASE_DIR

SCHEMA = """
CREATE TABLE IF NOT EXISTS predictions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at       TEXT DEFAULT CURRENT_TIMESTAMP,
    n                REAL NOT NULL,
    p                REAL NOT NULL,
    k                REAL NOT NULL,
    temperature      REAL NOT NULL,
    humidity         REAL NOT NULL,
    ph               REAL NOT NULL,
    rainfall         REAL NOT NULL,
    field_size_ha    REAL NOT NULL,
    predicted_crop   TEXT NOT NULL,
    confidence_pct   REAL NOT NULL,
    irrigation       TEXT
);
"""


def get_db_path() -> str:
    return os.getenv("AGROSMART_DB_PATH", os.path.join(BASE_DIR, "data", "agrosmart.db"))


def _connect() -> sqlite3.Connection:
    path = get_db_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA)
    return conn


def log_prediction(inputs: Dict[str, Any], crop: str, confidence_pct: float, irrigation: str) -> int:
    """Insert one prediction row and return its id."""
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO predictions "
            "(n, p, k, temperature, humidity, ph, rainfall, field_size_ha, "
            " predicted_crop, confidence_pct, irrigation) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                inputs["N"], inputs["P"], inputs["K"], inputs["temperature"],
                inputs["humidity"], inputs["ph"], inputs["rainfall"],
                inputs.get("field_size_hectares", 1.0), crop, confidence_pct, irrigation,
            ),
        )
        return cur.lastrowid


def recent_predictions(limit: int = 10) -> List[Dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM predictions ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def prediction_stats() -> Dict[str, Any]:
    """Aggregate statistics computed with SQL (COUNT, AVG, GROUP BY)."""
    with _connect() as conn:
        total = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
        by_crop = conn.execute(
            "SELECT predicted_crop AS crop, COUNT(*) AS count, "
            "       ROUND(AVG(confidence_pct), 1) AS avg_confidence_pct, "
            "       ROUND(AVG(rainfall), 1) AS avg_rainfall, "
            "       ROUND(AVG(ph), 2) AS avg_ph "
            "FROM predictions GROUP BY predicted_crop "
            "ORDER BY count DESC, crop ASC"
        ).fetchall()
    return {"total_predictions": total, "by_crop": [dict(r) for r in by_crop]}

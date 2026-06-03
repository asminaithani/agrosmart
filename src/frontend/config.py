"""Runtime configuration for the frontend-only AgroSmart app."""

import os


def _path_from_env(name: str, default: str) -> str:
    value = os.getenv(name, default).strip()
    return value if value.startswith("/") else f"/{value}"


API_BASE_URL = os.getenv(
    "AGROSMART_API_BASE_URL",
    os.getenv("BACKEND_URL", "http://localhost:8000"),
).rstrip("/")

PREDICT_ENDPOINT = _path_from_env("AGROSMART_PREDICT_ENDPOINT", "/api/predict")
CHAT_ENDPOINT = _path_from_env("AGROSMART_CHAT_ENDPOINT", "/api/chat")
HEALTH_ENDPOINT = _path_from_env("AGROSMART_HEALTH_ENDPOINT", "/api/health")

API_TIMEOUT_SECONDS = float(os.getenv("AGROSMART_API_TIMEOUT_SECONDS", "15"))

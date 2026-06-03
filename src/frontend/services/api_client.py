"""HTTP client boundary between the Streamlit UI and backend services."""

import requests
from typing import Optional

from config import (
    API_BASE_URL,
    API_TIMEOUT_SECONDS,
    CHAT_ENDPOINT,
    HEALTH_ENDPOINT,
    PREDICT_ENDPOINT,
)


class ApiClientError(Exception):
    """Raised when the backend contract cannot be fulfilled."""


def _url(path: str) -> str:
    return f"{API_BASE_URL}{path}"


def _json_or_error(response: requests.Response) -> dict:
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as exc:
        try:
            detail = response.json()
        except ValueError:
            detail = {"message": response.text or str(exc)}
        raise ApiClientError(f"Backend returned {response.status_code}: {detail}") from exc
    except ValueError as exc:
        raise ApiClientError("Backend returned invalid JSON.") from exc


def predict_crop(payload: dict) -> dict:
    """Send farm parameters to the backend prediction API."""
    try:
        response = requests.post(
            _url(PREDICT_ENDPOINT),
            json=payload,
            timeout=API_TIMEOUT_SECONDS,
        )
        return _json_or_error(response)
    except requests.exceptions.ConnectionError as exc:
        raise ApiClientError(
            "Cannot connect to backend. Check AGROSMART_API_BASE_URL and make sure the API is running."
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise ApiClientError("Backend request timed out. Try again or increase AGROSMART_API_TIMEOUT_SECONDS.") from exc
    except requests.exceptions.RequestException as exc:
        raise ApiClientError(f"Backend request failed: {exc}") from exc


def chat(message: str, farm_context: Optional[dict] = None) -> dict:
    """Send a farmer question and optional prediction context to the chat API."""
    try:
        response = requests.post(
            _url(CHAT_ENDPOINT),
            json={"message": message, "farm_context": farm_context or {}},
            timeout=max(API_TIMEOUT_SECONDS, 20),
        )
        return _json_or_error(response)
    except requests.exceptions.ConnectionError as exc:
        raise ApiClientError(
            "Cannot connect to chatbot backend. Check AGROSMART_API_BASE_URL and make sure the API is running."
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise ApiClientError("Chatbot request timed out.") from exc
    except requests.exceptions.RequestException as exc:
        raise ApiClientError(f"Chatbot request failed: {exc}") from exc


def health() -> dict:
    """Optional health check used by deployments and smoke tests."""
    try:
        response = requests.get(_url(HEALTH_ENDPOINT), timeout=5)
        return _json_or_error(response)
    except requests.exceptions.RequestException as exc:
        raise ApiClientError(f"Health check failed: {exc}") from exc

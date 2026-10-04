import logging
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.endpoints import router as api_router
from src.core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("agrosmart.api")

app = FastAPI(
    title="Climate-Smart Agriculture Assistant API",
    description="API for predicting optimal crops and recommending sustainable irrigation methods.",
    version="1.0.0"
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log method, path, status code and duration for every request."""
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        # Unhandled error: log the full traceback, return a clean JSON 500.
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"error": "Internal server error"})
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info("%s %s -> %s (%.0f ms)", request.method, request.url.path, response.status_code, duration_ms)
    return response


app.include_router(api_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "healthy"}

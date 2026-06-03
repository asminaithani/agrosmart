from fastapi import FastAPI
from src.api.endpoints import router as api_router

app = FastAPI(
    title="Climate-Smart Agriculture Assistant API",
    description="API for predicting optimal crops and recommending sustainable irrigation methods.",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first so this layer is cached until requirements.txt changes
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the project and train the model at build time so the image is self-contained
COPY . .
RUN python -m src.ml.train

# Run as a non-root user; /app/data holds the SQLite prediction log
RUN useradd --create-home appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

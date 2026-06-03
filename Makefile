SHELL := /bin/bash

.PHONY: setup install train analyze test run clean

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
UVICORN = $(VENV)/bin/uvicorn

setup:
	python3 -m venv $(VENV)

install: setup
	$(PIP) install -r requirements.txt

train:
	$(PYTHON) -m src.ml.train

analyze:
	$(PYTHON) -m src.ml.analyze

test:
	$(VENV)/bin/pytest tests/

run: run-backend run-frontend

run-backend:
	@echo "Starting FastAPI backend on port 8000..."
	$(UVICORN) src.api.main:app --host 0.0.0.0 --port 8000 &

run-frontend:
	@echo "Starting Streamlit frontend on port 8501..."
	$(PYTHON) -m streamlit run src/frontend/app.py --server.headless true --server.fileWatcherType none

clean:
	rm -rf __pycache__ .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf $(VENV)

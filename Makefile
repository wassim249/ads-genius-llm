.PHONY: help install lint format test clean run docker-build docker-run install-data-pipeline

# Default target executed when no arguments are given to make.
help:
	@echo "Available commands:"
	@echo "  help                 - Show this help message"
	@echo "  install              - Install production dependencies"
	@echo "  install-data-pipeline - Install data pipeline dependencies"
	@echo "  lint                 - Run linters (ruff, mypy)"
	@echo "  format               - Format code (black, isort)"
	@echo "  test                 - Run tests"
	@echo "  clean                - Remove build artifacts and cache directories"
	@echo "  run                  - Run the application locally"
	@echo "  docker-build         - Build Docker image"
	@echo "  docker-run           - Run application in Docker container"

# Install production dependencies
install:
	python -m venv .venv
	source .venv/bin/activate
	pip install -e .

# Install data pipeline dependencies
install-data-pipeline:
	pip install -r data/requirements.txt

# Run linters
lint:
	ruff check .
	mypy app

# Format code
format:
	black .
	isort .

# Run tests
test:
	# TODO: Add tests
	pytest -xvs tests/

# Clean build artifacts and cache directories
clean:
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache	
	find . -type d -name __pycache__ -exec rm -rf {} +

# Run the application locally
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Build Docker image
docker-build:
	# TODO: Add Docker build
	docker build -t ads-genius-ai:latest .

# Run application in Docker container
docker-run:
	# TODO: Add Docker build
	docker run -p 8000:8000 --env-file .env ads-genius-ai:latest 
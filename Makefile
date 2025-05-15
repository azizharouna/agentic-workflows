# Makefile for early development
.PHONY: install test format

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

format:
	black agents/ tests/
	isort agents/ tests/

lint:
	flake8 agents/ tests/

test-rate-limit:
	pytest tests/test_rate_limiter.py -v

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache .mypy_cache .coverage
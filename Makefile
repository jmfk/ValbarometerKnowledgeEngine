.PHONY: test test-backend test-frontend test-infra test-integration test-regression lint lint-backend lint-frontend

test: test-backend test-frontend test-infra test-integration test-regression lint

test-backend:
	@echo "Running backend tests..."
	pytest tests/

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm test -- --run

test-infra:
	@echo "Running infra tests..."
	pytest tests/test_infra.py

test-integration:
	@echo "Running integration tests..."
	pytest tests/integration/

test-regression:
	@echo "Running regression tests..."
	pytest tests/regression/

lint: lint-backend lint-frontend

lint-backend:
	@echo "Running backend linting..."
	ruff check vibe_tools/

lint-frontend:
	@echo "Running frontend linting..."
	cd frontend && npm run lint

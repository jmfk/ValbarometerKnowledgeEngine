.PHONY: install setup venv benchmark benchmark-list benchmark-case test lint help

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

help:
	@echo "Usage:"
	@echo "  make setup                              Create venv and install deps"
	@echo "  make install                            Install deps into existing venv"
	@echo "  make benchmark MODELS=m1,m2             Run benchmark on comma-separated models"
	@echo "  make benchmark MODELS=all               Run benchmark on ALL models"
	@echo "  make benchmark-case MODELS=m1 CASE=id   Run single test case"
	@echo "  make benchmark-list                     List available models"
	@echo "  make test                               Run pytest"
	@echo "  make lint                               Run ruff linter"

setup: venv install
	@echo "Done. Activate with: source $(VENV)/bin/activate"

venv:
	@test -d $(VENV) || python3 -m venv $(VENV)

install: venv
	$(PIP) install -r benchmarks/claim_extraction/requirements.txt

_RESOLVE_MODELS = $(if $(filter all,$(MODELS)),$(shell $(PYTHON) -c "from benchmarks.claim_extraction.config import MODELS; print(','.join(MODELS))"),$(MODELS))

benchmark: install
ifndef MODELS
	$(error Usage: make benchmark MODELS=gemini-2.5-flash,gpt-4o-mini  (or MODELS=all))
endif
	@for model in $$(echo $(_RESOLVE_MODELS) | tr ',' ' '); do \
		echo "=== Benchmarking $$model ==="; \
		$(PYTHON) -m benchmarks.claim_extraction.run_benchmark --model $$model; \
	done

benchmark-list: install
	@$(PYTHON) -m benchmarks.claim_extraction.run_benchmark --list-models

benchmark-case: install
ifndef MODELS
	$(error Usage: make benchmark-case MODELS=gemini-2.5-flash CASE=case_01)
endif
ifndef CASE
	$(error Usage: make benchmark-case MODELS=gemini-2.5-flash CASE=case_01)
endif
	@for model in $$(echo $(MODELS) | tr ',' ' '); do \
		echo "=== Benchmarking $$model on $(CASE) ==="; \
		$(PYTHON) -m benchmarks.claim_extraction.run_benchmark --model $$model --case $(CASE); \
	done

test: install
	$(VENV)/bin/pytest tests/

lint: install
	$(VENV)/bin/ruff check benchmarks/

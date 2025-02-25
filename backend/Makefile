MAKEFLAGS += --silent

PYTHON_CMD ?= python3
POETRY_CMD ?= $(shell command -v poetry)

.PHONY: check-python check-poetry init-poetry-shell install prisma-generate prisma-db-push run-server run-doc-agent run-event-api

check-python:
	@if [ -z "$(PYTHON_CMD)" ]; then \
		echo "No Python interpreter found. Please install Python 3."; \
		exit 1; \
	else \
		echo "Using Python: $(PYTHON_CMD)"; \
	fi

check-poetry: check-python
	@if [ -z "$(POETRY_CMD)" ]; then \
		echo "Poetry is not installed. Installing Poetry..."; \
		$(PYTHON_CMD) -m pip install --user poetry || { echo "Failed to install Poetry. Please install it manually."; exit 1; }; \
	else \
		echo "Using Poetry: $(POETRY_CMD)"; \
	fi

install: check-poetry
	@echo "Installing dependencies within Poetry shell..."
	poetry install

prisma-generate: install
	@echo "Generating Prisma client..."
	poetry run prisma generate

prisma-db-push: prisma-generate
	@echo "Pushing Prisma schema to the database..."
	poetry run prisma db push

run-event-api: install
	@echo "Starting event-api.py..."
	poetry run python3 api/event-api.py

run-server: install
	@echo "Starting server.py..."
	poetry run python3 server.py

run-doc-agent: install
	@echo "Starting doc-agent.py..."
	poetry run python3 doc-agent.py

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
	$(POETRY_CMD) install

prisma-generate: install
	@echo "Generating Prisma client..."
	$(POETRY_CMD) run prisma generate

prisma-db-push: prisma-generate
	@echo "Pushing Prisma schema to the database..."
	$(POETRY_CMD) run prisma db push

run: install
	@echo "Running the backend project..."
	$(POETRY_CMD) run $(PYTHON_CMD) main.py

run-g4f-server: install
	@echo "Starting g4f server..."
	$(POETRY_CMD) run $(PYTHON_CMD) -m g4f.api.run

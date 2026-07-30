COMPOSE := docker compose --env-file .env.example
MIN_FREE_MB ?= 20000
WAIT_TIMEOUT ?= 240

.PHONY: preflight up down restart logs backend flutter shell-backend shell-db lint format test db-upgrade db-downgrade db-current db-history db-revision create-company check-task

preflight:
	@echo "Checking Docker daemon..."
	@docker info >/dev/null
	@echo "Checking Docker Compose configuration..."
	@$(COMPOSE) config >/dev/null
	@available_mb=$$(df -Pm . | awk 'NR==2 {print $$4}'); \
	if [ "$$available_mb" -lt "$(MIN_FREE_MB)" ]; then \
		echo "Not enough free disk space for Docker development stack."; \
		echo "Available: $${available_mb} MB"; \
		echo "Required:  $(MIN_FREE_MB) MB"; \
		echo "Free disk space or run with MIN_FREE_MB=<value> make up."; \
		exit 1; \
	fi
	@echo "Preflight OK."

up: preflight
	$(COMPOSE) up -d --build --wait --wait-timeout $(WAIT_TIMEOUT)

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) restart

logs:
	$(COMPOSE) logs -f

backend: preflight
	$(COMPOSE) up -d --build --wait --wait-timeout $(WAIT_TIMEOUT) backend

flutter: preflight
	$(COMPOSE) up -d --build --wait --wait-timeout $(WAIT_TIMEOUT) frontend

shell-backend:
	$(COMPOSE) exec backend sh

shell-db:
	$(COMPOSE) exec postgres sh -lc 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'

db-upgrade:
	$(COMPOSE) exec backend alembic upgrade head

db-downgrade:
	$(COMPOSE) exec backend alembic downgrade -1

db-current:
	$(COMPOSE) exec backend alembic current

db-history:
	$(COMPOSE) exec backend alembic history

db-revision:
	@if [ -z "$(name)" ]; then echo 'Usage: make db-revision name="descricao"'; exit 1; fi
	$(COMPOSE) exec backend alembic revision --autogenerate -m "$(name)"

create-company:
	@if [ -z "$(COMPANY_LEGAL_NAME)" ] || [ -z "$(COMPANY_TRADE_NAME)" ] || [ -z "$(COMPANY_DOCUMENT)" ] || [ -z "$(COMPANY_SLUG)" ] || [ -z "$(COMPANY_CODE)" ]; then \
		echo 'Usage: COMPANY_LEGAL_NAME="..." COMPANY_TRADE_NAME="..." COMPANY_DOCUMENT="11222333000181" COMPANY_SLUG="empresa" COMPANY_CODE="EMPRESA" make create-company'; \
		exit 1; \
	fi
	$(COMPOSE) exec \
		-e COMPANY_LEGAL_NAME="$(COMPANY_LEGAL_NAME)" \
		-e COMPANY_TRADE_NAME="$(COMPANY_TRADE_NAME)" \
		-e COMPANY_DOCUMENT="$(COMPANY_DOCUMENT)" \
		-e COMPANY_EMAIL="$(COMPANY_EMAIL)" \
		-e COMPANY_PHONE="$(COMPANY_PHONE)" \
		-e COMPANY_SLUG="$(COMPANY_SLUG)" \
		-e COMPANY_CODE="$(COMPANY_CODE)" \
		-e COMPANY_TIMEZONE="$(COMPANY_TIMEZONE)" \
		-e COMPANY_LOCALE="$(COMPANY_LOCALE)" \
		-e COMPANY_CURRENCY="$(COMPANY_CURRENCY)" \
		backend python -m app.modules.companies.infrastructure.bootstrap

lint:
	$(COMPOSE) run --rm backend ruff check app tests
	$(COMPOSE) run --rm frontend sh -lc 'git config --global --add safe.directory /sdks/flutter && flutter pub get && flutter analyze'

format:
	$(COMPOSE) run --rm backend ruff format app tests
	$(COMPOSE) run --rm frontend sh -lc 'git config --global --add safe.directory /sdks/flutter && flutter pub get && dart format lib test'

test:
	$(COMPOSE) run --rm backend pytest
	$(COMPOSE) run --rm frontend sh -lc 'git config --global --add safe.directory /sdks/flutter && flutter pub get && flutter test'

check-task:
	@if [ -z "$(TASK)" ]; then echo 'Usage: make check-task TASK=DEV-008'; exit 1; fi
	python3 scripts/check_task_compliance.py --task "$(TASK)"

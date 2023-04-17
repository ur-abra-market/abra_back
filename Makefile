application_directory := app
code_directory := $(application_directory)

compose_application := docker compose -f docker-compose.app.yml -f docker-compose.db.yml
compose_migrations := docker compose -f docker-compose.alembic.yml -f docker-compose.db.yml

.PHONY: clean
clean:
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf {.cache,.ruff_cache,.mypy_cache}

.PHONY: lint
lint:
	isort --check-only $(code_directory)
	black --check --diff $(code_directory)
	ruff $(code_directory)
	mypy $(code_directory)

.PHONY: reformat
reformat:
	black $(code_directory)
	isort $(code_directory)
	ruff --fix $(code_directory)

.PHONY: build
build:
	$(compose_application) build

.PHONY: up
up:
	$(compose_application) up

.PHONY: logs
logs:
	$(compose_application) logs -f

.PHONY: stop
stop:
	$(compose_application) stop
	$(compose_migrations) stop

.PHONY: down
down:
	$(compose_application) down
	$(compose_migrations) down

.PHONY: restart
restart:
	$(compose_application) stop
	$(compose_application) up -d

.PHONY: destroy
destroy:
	$(compose_application) down -v
	$(compose_migrations) down -v

.PHONY: migrations_build
migrations_build:
	$(compose_migrations) build

.PHONY: migrations
migrations:
	$(compose_migrations) up -d

.PHONY: migrations_logs
migrations_logs:
	$(compose_migrations) logs -f

.PHONY: exec
exec:
	$(compose_application) exec $(container) /bin/bash

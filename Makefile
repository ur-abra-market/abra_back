application_directory = app
tests_directory = tests
code_directory = $(application_directory) $(tests_directory)

compose_application = docker compose -f docker-compose.app.yml -f docker-compose.db.yml
compose_tests = docker compose -f docker-compose.tests.yml -f docker-compose.db.yml
compose_migrations = docker compose -f docker-compose.alembic.yml -f docker-compose.db.yml

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
	mypy $(application_directory)

.PHONY: reformat
reformat:
	black $(code_directory)
	isort $(code_directory)
	ruff --fix $(code_directory)

.PHONY: build
build:
	$(compose_application) build
	$(compose_tests) build
	$(compose_migrations) build


.PHONY: up
up:
	$(compose_application) up -d

.PHONY: logs
logs:
	$(compose_application) logs -f

.PHONY: stop
stop:
	$(compose_application) stop
	$(compose_tests) stop
	$(compose_migrations) stop

.PHONY: down
down:
	$(compose_application) down
	$(compose_tests) down
	$(compose_migrations) down

.PHONY: restart
restart:
	$(compose_application) stop
	$(compose_application) up -d

.PHONY: destroy
destroy:
	$(compose_application) down -v
	$(compose_tests) down -v
	$(compose_migrations) down -v

.PHONY: build_tests
build_tests:
	$(compose_tests) build

.PHONY: tests
tests:
	$(compose_tests) up -d

.PHONY: restart_tests
restart_tests:
	$(compose_tests) stop
	$(compose_tests) up -d

.PHONY: logs_tests
logs_tests:
	$(compose_tests) logs -f

.PHONY: build_migrations
build_migrations:
	$(compose_migrations) build

.PHONY: migrations
migrations:
	$(compose_migrations) up -d


.PHONY: restart_migrations
restart_migrations:
	$(compose_migrations) stop
	$(compose_migrations) up -d

.PHONY: logs_migrations
logs_migrations:
	$(compose_migrations) logs -f

.PHONY: exec
exec:
	$(compose_application) exec $(container) /bin/bash

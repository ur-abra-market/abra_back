application_directory = app
population_directory = population
tests_directory = tests
code_directory = $(application_directory) $(population_directory) $(tests_directory)

compose_application = docker compose -f docker-compose.app.yml -f docker-compose.db.yml
compose_population = docker compose -f docker-compose.population.yml -f docker-compose.db.yml
compose_tests = docker compose -f docker-compose.tests.yml -f docker-compose.tests.db.yml
compose_migrations = docker compose -f docker-compose.alembic.yml -f docker-compose.db.yml

# =============================================SYSTEM=============================================
.PHONY: clean
clean:
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf {.cache,.ruff_cache,.mypy_cache}
# =============================================SYSTEM=============================================

# ==============================================CODE==============================================
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
# ==============================================CODE==============================================

# ======================================DOCKER(COMMON RULES)======================================
.PHONY: build
build:
	$(compose_application) build
	$(compose_population) build
	$(compose_tests) build
	$(compose_migrations) build

.PHONY: stop
stop:
	$(compose_application) stop
	$(compose_population) stop
	$(compose_tests) stop
	$(compose_migrations) stop

.PHONY: down
down:
	$(compose_application) down
	$(compose_population) down
	$(compose_tests) down
	$(compose_migrations) down

.PHONY: destroy
destroy:
	$(compose_application) down -v
	$(compose_population) down -v
	$(compose_tests) down -v
	$(compose_migrations) down -v

.PHONY: exec
exec:
	$(compose_application) exec $(container) /bin/bash
# ======================================DOCKER(COMMON RULES)======================================

# ==========================================DOCKER(APP)===========================================
.PHONY: build-application
build-application:
	$(compose_application) build

.PHONY: application
application:
	$(compose_application) up -d

.PHONY: stop-application
stop-application:
	$(compose_application) stop

.PHONY: down-application
down-application:
	$(compose_application) down

.PHONY: destroy-application
destroy-application:
	$(compose_application) down -v

.PHONY: restart-application
restart-application:
	$(compose_application) stop
	$(compose_application) up -d

.PHONY: application-logs
application-logs:
	$(compose_application) logs -f
# ==========================================DOCKER(APP)===========================================

# ========================================DOCKER(POPULATION)======================================
.PHONY: build-population
build-population:
	$(compose_population) build

.PHONY: population
population:
	$(compose_population) up

.PHONY: stop-population
stop-population:
	$(compose_population) stop

.PHONY: down-population
down-population:
	$(compose_population) down

.PHONY: destroy-population
destroy-population:
	$(compose_population) down -v

.PHONY: restart-population
restart-population:
	$(compose_population) stop
	$(compose_population) up -d

.PHONY: population-logs
population-logs:
	$(compose_population) logs -f
# ========================================DOCKER(POPULATION)======================================

# ==========================================DOCKER(TESTS)=========================================
.PHONY: build-tests
build-tests:
	$(compose_tests) build

.PHONY: tests
tests:
	$(compose_tests) up

.PHONY: stop-tests
stop-tests:
	$(compose_tests) stop

.PHONY: down-tests
down-tests:
	$(compose_tests) down

.PHONY: destroy-tests
destroy-tests:
	$(compose_tests) down -v

.PHONY: restart-tests
restart-tests:
	$(compose_tests) stop
	$(compose_tests) up -d

.PHONY: tests-logs
tests-logs:
	$(compose_tests) logs -f
# ==========================================DOCKER(TESTS)=========================================

# ========================================DOCKER(MIGRATIONS)======================================
.PHONY: build-migrations
build-migrations:
	$(compose_migrations) build

.PHONY: migrations
migrations:
	$(compose_migrations) up -d

.PHONY: stop-migrations
stop-migrations:
	$(compose_migrations) stop

.PHONY: down-migrations
down-migrations:
	$(compose_migrations) down

.PHONY: destroy-migrations
destroy-migrations:
	$(compose_migrations) down -v

.PHONY: restart-migrations
restart-migrations:
	$(compose_migrations) stop
	$(compose_migrations) up -d

.PHONY: migrations-logs
migrations-logs:
	$(compose_migrations) logs -f
# ========================================DOCKER(MIGRATIONS)======================================

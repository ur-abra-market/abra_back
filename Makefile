# ============================================VARIABLES===========================================
docker_v2 = docker compose

application_directory = app
compose_directory = docker/compose
population_directory = population
tests_directory = tests
code_directory = $(application_directory) $(population_directory) $(tests_directory)

capture_exit_code = --abort-on-container-exit --exit-code-from
exit_code_population = population
exit_code_tests = tests
exit_code_migrations = alembic

compose_application = $(docker_v2) -f $(compose_directory)/app.yml -f $(compose_directory)/db.yml --env-file .env
compose_population = $(docker_v2) -f $(compose_directory)/population.yml -f $(compose_directory)/db.yml --env-file .env
compose_tests = $(docker_v2) -f $(compose_directory)/tests.yml -f $(compose_directory)/tests.db.yml --env-file .env
compose_migrations = $(docker_v2) -f $(compose_directory)/alembic.yml -f $(compose_directory)/db.yml --env-file .env
# ============================================VARIABLES===========================================

# =============================================SYSTEM=============================================
.PHONY: clean
clean:
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf {.cache,.ruff_cache,.mypy_cache,.coverage,htmlcov,.pytest_cache}
# =============================================SYSTEM=============================================

# ==============================================CODE==============================================
.PHONY: lint
lint:
	isort --check-only $(code_directory)
	black --check --diff $(code_directory)
	ruff $(code_directory)
	mypy $(application_directory) $(population_directory)

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

.PHONE: applicationd
applicationd:
	$(compose_application) up

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
	$(compose_population) up $(capture_exit_code) $(exit_code_population)

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
	$(compose_population) up $(capture_exit_code) $(exit_code_population)

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
	$(compose_tests) up $(capture_exit_code) $(exit_code_tests)

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
	$(compose_tests) up $(capture_exit_code) $(exit_code_tests)

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
	$(compose_migrations) up $(capture_exit_code) $(exit_code_migrations)

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
	$(compose_migrations) up $(capture_exit_code) $(exit_code_migrations)

.PHONY: migrations-logs
migrations-logs:
	$(compose_migrations) logs -f
# ========================================DOCKER(MIGRATIONS)======================================

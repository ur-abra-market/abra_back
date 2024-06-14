#TODO ======================================= VARIABLES ========================================

docker_v2 = docker compose

# directories
application_directory = app
local_compose_directory = docker/compose/local
prod_compose_directory = docker/compose/prod
population_directory = population
tests_directory = tests
code_directory = $(application_directory) $(population_directory) $(tests_directory)

# local services
local_header = -f $(local_compose_directory)/header.yml
local_app_service = -f $(local_compose_directory)/app.yml
local_db_service = -f $(local_compose_directory)/db.yml
local_alembic_service = -f $(local_compose_directory)/alembic.yml
local_population_service = -f $(local_compose_directory)/population.yml
local_tests_service = -f $(local_compose_directory)/tests.yml
local_tests_db_service = -f $(local_compose_directory)/tests.db.yml
local_redis_service = -f $(local_compose_directory)/redis.yml
local_worker_service = -f $(local_compose_directory)/worker.yml

# prod services
prod_header_backend = -f $(prod_compose_directory)/header_backend.yml
prod_header_db = -f $(prod_compose_directory)/header_db.yml
prod_app_service = -f $(prod_compose_directory)/app.yml
prod_db_service = -f $(prod_compose_directory)/db.yml
prod_alembic_service = -f $(prod_compose_directory)/alembic.yml
prod_redis_service = -f $(prod_compose_directory)/redis.yml
prod_worker_service = -f $(prod_compose_directory)/worker.yml

# exit codes
capture_exit_code = --abort-on-container-exit --exit-code-from
exit_code_population = population
exit_code_tests = tests
exit_code_migrations = alembic

# local templates
local_application = $(docker_v2) ${local_header} ${local_app_service} ${local_redis_service} ${local_db_service} ${local_worker_service} --env-file .env
local_database = $(docker_v2) ${local_header} ${local_db_service} --env-file .env
local_migrations = $(docker_v2) ${local_header} ${local_alembic_service} ${local_db_service} --env-file .env
local_population = $(docker_v2) ${local_header} ${local_population_service} ${local_db_service} --env-file .env
local_tests = $(docker_v2) ${local_header} ${local_tests_service} ${local_tests_db_service} --env-file .env

# prod templates
prod_database = $(docker_v2) ${prod_header_db} ${prod_db_service} --env-file .env
prod_application = $(docker_v2) ${prod_header_backend} ${prod_app_service} ${prod_redis_service} ${prod_worker_service} --env-file .env
prod_migrations = $(docker_v2) ${prod_header_db} ${prod_alembic_service} --env-file .env
prod_population = $(docker_v2) ${prod_header_db} ${prod_population_service} --env-file .env


name = application

# ==========================================================================================


#TODO ========================================= SYSTEM =========================================

.PHONY: clean
clean:
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf `find . -type d -name '__pycache__' -o -name '.cache' -o -name '.ruff_cache' -o -name '.mypy_cache' -o -name '.coverage' -o -name 'htmlcov' -o -name '.pytest_cache'`

.PHONY: prune
prune:
	docker system prune --all --force --volumes

# ==========================================================================================


#TODO ========================================== CORE ==========================================

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

# ==========================================================================================


#TODO ====================================== ENVIRONMENT =======================================

.PHONY: exec
exec:
	compose_$(name) exec $(container) /bin/bash

# ==========================================================================================


#TODO ========================================= LOCAL ==========================================


# common rules
.PHONY: build
build:
	$(local_application) build
	$(local_population) build
	$(local_migrations) build

.PHONY: stop
stop:
	$(local_application) stop
	$(local_population) stop
	$(local_migrations) stop

.PHONY: down
down:
	$(local_application) down
	$(local_population) down
	$(local_tests) down
	$(local_migrations) down

.PHONY: destroy
destroy:
	$(local_application) down -v
	$(local_population) down -v
	$(local_tests) down -v
	$(local_migrations) down -v


# application
.PHONY: build application
application_build:
	$(local_application) build

.PHONY: application
application:
	$(local_application) up

.PHONE: application in detach mode
application_detached:
	$(local_application) up -d

.PHONY: stop-application
application_stop:
	$(local_application) stop

.PHONY: down-application
application_down:
	$(local_application) down

.PHONY: destroy-application
application_destroy:
	$(local_application) down -v

.PHONY: restart-application
application_restart:
	$(local_application) stop
	$(local_application) up -d

.PHONY: application-logs
application_logs:
	$(local_application) logs -f


# database
.PHONY: up database
database:
	${local_database} up -d

.PHONY: stop database
database_stop:
	${local_database} stop


# migrations
.PHONY: build-migrations
migrations_build:
	$(local_migrations) build

.PHONY: migrations
migrations:
	$(local_migrations) up $(capture_exit_code) $(exit_code_migrations)

.PHONY: stop-migrations
migrations_stop:
	$(local_migrations) stop

.PHONY: down-migrations
migrations_down:
	$(local_migrations) down

.PHONY: destroy-migrations
migrations_destroy:
	$(local_migrations) down -v

.PHONY: restart-migrations
migrations_restart:
	$(local_migrations) stop
	$(local_migrations) up $(capture_exit_code) $(exit_code_migrations)

.PHONY: migrations-logs
migrations_logs:
	$(local_migrations) logs -f


# population
.PHONY: build-population
population_build:
	$(local_population) build

.PHONY: population
population:
	$(local_population) up $(capture_exit_code) $(exit_code_population)

.PHONY: stop-population
population_stop:
	$(local_population) stop

.PHONY: down-population
population_down:
	$(local_population) down

.PHONY: destroy-population
population_destroy:
	$(local_population) down -v

.PHONY: restart-population
population_restart:
	$(local_population) stop
	$(local_population) up $(capture_exit_code) $(exit_code_population)

.PHONY: population-logs
population_logs:
	$(local_population) logs -f


# tests
.PHONY: build-tests
tests_build:
	$(local_tests) build

.PHONY: tests
tests:
	$(local_tests) up $(capture_exit_code) $(exit_code_tests)

.PHONY: stop-tests
tests_stop:
	$(local_tests) stop

.PHONY: down-tests
tests_down:
	$(local_tests) down

.PHONY: destroy-tests
tests_destroy:
	$(local_tests) down -v

.PHONY: restart-tests
tests_restart:
	$(local_tests) stop
	$(local_tests) up $(capture_exit_code) $(exit_code_tests)

.PHONY: tests-logs
tests_logs:
	$(local_tests) logs -f


# ==========================================================================================




#TODO ========================================== PROD ==========================================


# application
.PHONY: build application for prod environment
prod_application_build:
	$(prod_application) build

.PHONY: run application for prod environment
prod_application_run:
	$(prod_application) up

.PHONE: run application in detach mode for prod environment
prod_application_run_detached:
	$(prod_application) up -d

.PHONY: stop application for prod environment
prod_application_stop:
	$(prod_application) stop

.PHONY: remove application container for prod environment
prod_application_down:
	$(prod_application) down

.PHONY: remove application container and volumes for prod environment
prod_application_destroy:
	$(prod_application) down -v

.PHONY: restart application for prod environment
prod_application_restart:
	$(prod_application) stop
	$(prod_application) up -d

.PHONY: check logs for application for prod environment
prod_application_logs:
	$(prod_application) logs -f


# database
.PHONY: run database for prod environment
prod_database_run:
	${prod_database} up

.PHONY: run database in detached mode for prod environment
prod_database_run_detached:
	${prod_database} up -d

.PHONY: stop database for prod environment
prod_database_stop:
	${prod_database} stop


# migrations
.PHONY: run migrations for prod environment
prod_migrations_run:
	$(prod_migrations) build
	$(prod_migrations) up $(capture_exit_code) $(exit_code_migrations)

.PHONY: stop migrations for prod environment
prod_migrations_stop:
	$(prod_migrations) stop

.PHONY: remove migrations container for prod environment
prod_migrations_down:
	$(prod_migrations) down

.PHONY: remove migrations container and volumes for prod environment
prod_migrations_destroy:
	$(prod_migrations) down -v

.PHONY: restart migrations for prod environment
prod_migrations_restart:
	$(prod_migrations) stop
	$(prod_migrations) up $(capture_exit_code) $(exit_code_migrations)

.PHONY: check migrations logs for prod environment
prod_migrations_logs:
	$(prod_migrations) logs -f


# ==========================================================================================

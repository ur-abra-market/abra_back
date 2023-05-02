#!/bin/bash

export PROJECT_PATH=$(pwd)

head -n -2 ./docker/compose/app.prod.yml > docker-compose.yml
tail --lines=+4 ./docker/compose/alembic.yml >> docker-compose.yml
tail --lines=+4 ./docker/compose/population.dev.yml | head -n -2 ./docker/compose/population.dev.yml >> docker-compose.yml
echo -e "\n" >> docker-compose.yml
tail --lines=-2 ./docker/compose/app.prod.yml >> docker-compose.yml

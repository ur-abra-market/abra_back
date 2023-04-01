#!/bin/bash

cat docker-compose.yml docker-compose.alembic.yml > docker-compose.new.yml
mv docker-compose.new.yml docker-compose.yml
rm docker-compose.alembic.yml docker-compose.db.yml

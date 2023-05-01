#!/bin/bash

head -n -2 docker-compose.app.prod.yml > docker-compose.yml
echo -e "\n" >> docker-compose.yml
tail --lines=+4 docker-compose.alembic.yml >> docker-compose.yml
tail --lines=+2 docker-compose.app.prod.yml >> docker-compose.yml
rm docker-compose.alembic.yml docker-compose.db.yml docker-compose.app.yml docker-compose.app.prod.yml

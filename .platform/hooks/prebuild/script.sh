#!/bin/bash

mv ./docker/compose/dev.yml ./docker-compose.yml
# mv ./docker/Dockerfile ./Dockerfile
sudo chmod 775 ./docker-compose.yml
# sudo chmod 775 ./Dockerfile
ls -la

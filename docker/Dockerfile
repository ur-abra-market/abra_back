FROM python:latest

WORKDIR /app

ADD . /app

RUN python -m pip install --upgrade pip
RUN python -m pip install poetry
RUN python -m poetry config virtualenvs.create false && \
    python -m poetry install --no-interaction --no-ansi

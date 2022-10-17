FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update

WORKDIR /api
EXPOSE 8000

COPY /app ./app
COPY /main.py ./main.py
COPY /requirements.txt ./requirements.txt

RUN python -m venv /.venv && \
    /.venv/bin/pip install --upgrade pip && \
    /.venv/bin/pip install -r /api/requirements.txt && \
    adduser --disabled-password --no-create-home app

ENV PATH="/.venv/bin:$PATH"

USER app
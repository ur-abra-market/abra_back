FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update

WORKDIR /api
EXPOSE 8000

RUN python -m pip install --upgrade pip

COPY /requirements.txt ./requirements.txt
RUN pip install -r /api/requirements.txt

COPY /app ./app
COPY /main.py ./main.py

RUN adduser --disabled-password --no-create-home app

ENV PATH="/.venv/bin:$PATH"

USER app
FROM python:3.11.1

ENV PATH="${PATH}:/root/.poetry/bin"

WORKDIR /app

ADD . /app

RUN python -m pip install --upgrade pip
RUN python -m pip install poetry
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

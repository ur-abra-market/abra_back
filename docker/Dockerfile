FROM python:3.11.1

ENV PATH="${PATH}:/root/.poetry/bin"

WORKDIR /app

COPY pyproject.toml /app/

RUN python -m pip install --upgrade pip \
  && python -m pip install poetry \
  && poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --without dev

ADD . /app

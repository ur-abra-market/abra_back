FROM python:3.8.10-slim-buster

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /api
EXPOSE 8000

RUN python -m pip install --upgrade pip

COPY /requirements.txt ./requirements.txt
RUN pip install -r /api/requirements.txt

COPY /app ./app
COPY /main.py ./main.py

RUN adduser --disabled-password --no-create-home app

ENV PATH=/app/.local/bin:$PATH

USER app
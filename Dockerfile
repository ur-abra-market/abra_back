FROM python:3.8-slim-buster

RUN apt-get update

WORKDIR /api

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./

ENV PYTHONPATH=/:/api

CMD ["python", "main.py"]

# Change this line in main to enable auto-reload when code is modified
# uvicorn.run("logic.router:app", host="0.0.0.0", port=8000, reload=True)
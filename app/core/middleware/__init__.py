from fastapi import FastAPI

from .cors import setup_cors_middleware


def setup(app: FastAPI) -> None:
    setup_cors_middleware(app=app)

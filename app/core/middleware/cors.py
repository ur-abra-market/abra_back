from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.settings import cors_settings


def setup_cors_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_settings.ALLOW_ORIGINS,
        allow_credentials=cors_settings.ALLOW_CREDENTIALS,
        allow_methods=cors_settings.ALLOW_METHODS,
        allow_headers=cors_settings.ALLOW_HEADERS,
    )

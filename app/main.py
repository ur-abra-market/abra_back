from __future__ import annotations

import uvicorn

from core.settings import application_settings, fastapi_uvicorn_settings
from logger import logger


def main() -> None:
    logger.info(f"Starting application. Uvicorn running on {application_settings.URL}")

    uvicorn.run(
        app="app:app",
        host=fastapi_uvicorn_settings.HOSTNAME,
        port=fastapi_uvicorn_settings.PORT,
        reload=fastapi_uvicorn_settings.RELOAD,
    )


if __name__ == "__main__":
    main()

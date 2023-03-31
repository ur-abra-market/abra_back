import uvicorn
from loguru import logger

from core.settings import logging_settings, uvicorn_settings


def main() -> None:
    log_config = (
        None if logging_settings.CUSTOM_LOGGING_ON else uvicorn.config.LOGGING_CONFIG
    )
    logger.info(
        f"Starting application. Uvicorn running on http(s)://{uvicorn_settings.HOSTNAME}:{uvicorn_settings.PORT} "
    )
    logger.info(f"Custom logging on: {logging_settings.CUSTOM_LOGGING_ON}")
    uvicorn.run(
        app="app:app",
        host=uvicorn_settings.HOSTNAME,
        port=uvicorn_settings.PORT,
        reload=uvicorn_settings.RELOAD,
        log_config=log_config,
    )


if __name__ == "__main__":
    main()

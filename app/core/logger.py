import logging

import colorlog

from .settings import fastapi_settings

LOG_LEVEL = logging.DEBUG if fastapi_settings.DEBUG else logging.ERROR


def setup_logger() -> None:
    setup_general_logging()
    setup_sqlalchemy_logging()


def setup_general_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            fmt="%(log_color)s%(levelname)s%(reset)s \t\t | %(asctime)s.%(msecs)03d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(handler)


def setup_sqlalchemy_logging() -> None:
    logging.getLogger("sqlalchemy.engine").setLevel(LOG_LEVEL)
    logging.getLogger("sqlalchemy.pool").setLevel(LOG_LEVEL)

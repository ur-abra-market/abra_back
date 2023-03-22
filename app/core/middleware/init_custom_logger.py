import logging
import sys
from typing import Any

from core.settings import logging_settings
from loguru import logger

logger.remove()


class InterceptHandler(logging.Handler):
    """Default handler from loguru documentaion.

    https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def stdout_fomatter(record: dict[dict, Any], **kw) -> str:
    """Log format for stdout.

    Extra contains kw params passed into logging function -> logger.info('hi', profile='user_1')
    """

    base_info = "<green>{time:HH:mm:ss}</green> | {level} | <level>{message}</level>"

    if record["extra"]:
        # remove fields only needed in json logs
        record["extra"].pop("request_id", None)

        record["extra"] = "".join([f" {k}={v} " for k, v in record["extra"].items()])
        base_info += "<level>{extra}</level>"

    python_info = " file = {file.path}; function = {function}; line = {line};"
    info = base_info + python_info
    return info + "\n"


def json_formatter(record: dict, **kw) -> str:
    """Log format for json."""
    base_format = "{time:HH:mm:ss} {level} {message} {extra}"
    return base_format + "\n"


def json_filter(record: dict, *kwargs) -> bool:
    """Prevents exception from being recorded twice.
    Exception that we need contains record['extra'] because we raise it in logging_middleware.
    """
    if record["exception"] and not record["extra"]:
        return False
    return True


def init_custom_logging() -> None:
    """Replaces logging handlers with a handler for using the custom handler."""

    # intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(logging_settings.LOGGING_LEVEL)

    # remove every other logger's handlers
    # and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # set json handler
    logger.add(
        sink=logging_settings.LOGGING_FILE_PATH,
        format=json_formatter,
        level=logging_settings.LOGGING_LEVEL,
        serialize=True,
        encoding="utf-8",
        catch=False,
        filter=json_filter,
        enqueue=True,
        backtrace=True,
    )

    # set stdout handler
    logger.add(
        sink=sys.stdout,
        diagnose=True,
        colorize=True,
        level=logging_settings.LOGGING_LEVEL,
        format=stdout_fomatter,
        catch=False,
        backtrace=True,
    )

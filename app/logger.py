import logging
import colorlog
from pythonjsonlogger import jsonlogger

from core.settings import logging_settings

logger = logging.getLogger("abra")
logger.setLevel(logging_settings.LOGGING_LEVEL)

stream_handler = colorlog.StreamHandler()
stream_handler.setLevel(logging_settings.LOGGING_LEVEL)

formatter = colorlog.ColoredFormatter(
    fmt="[%(purple)s%(asctime)-s%(reset)s] - [%(log_color)s%(levelname)-s%(reset)s]- [%(log_color)s%(threadName)s] - [%(name)s%(reset)s] - %(blue)s%(filename)s:%(funcName)s:%(lineno)-d%(reset)s - %(message_log_color)s%(message)-s%(reset)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "FATAL": "white,bg_black",
        "CRITICAL": "red,bg_white",
    },
    secondary_log_colors={
        "message": {
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "FATAL": "white,bg_black",
            "CRITICAL": "red,bg_white",
        }
    }

)
stream_handler.setFormatter(formatter)

file_handler = logging.FileHandler(logging_settings.LOGGING_FILE_PATH)
file_handler.setLevel(logging_settings.LOGGING_LEVEL)

json_formatter = jsonlogger.JsonFormatter(
    fmt="[%(asctime)s] - [%(levelname)s] - [%(threadName)s] - [%(name)s] - %(filename)s:%(funcName)s:%(lineno)s - %(message)s",
)
file_handler.setFormatter(json_formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

logging.basicConfig(
    level=logging_settings.LOGGING_LEVEL,
    handlers=[stream_handler, file_handler],
)

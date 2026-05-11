"""
The module list the function to create a logger object to be used across modules for logging purposes
"""

import logging
from logging.handlers import RotatingFileHandler
from app.core.config import get_settings
from colorlog import ColoredFormatter

settings = get_settings()
LOG_LEVEL = "DEBUG" if settings.ENV.lower() == "dev" else "INFO"


def get_logger(name: str):
    """
    returns the logging.logger object with the following configuration:
        format: (time - module_name - levelname - message)
            color-code:
                - DEBUG: cyan
                - INFO: green
                - WARNING: yellow
                - ERROR: red
                - CRITICAL: bold_red
        handlers:
            - console handler: consoles the log on stdio
            - file hndler: appends the logs in server.log file (max_file_size = 1MB,backup_count = 3)
    """
    logger = logging.getLogger(name=name)

    # set log level
    logger.setLevel(LOG_LEVEL)

    # log format
    log_format = logging.Formatter(
        ColoredFormatter(
            fmt=" {asctime} - {name} - {levelname} - {message}",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
    )

    # define handlers
    stream_handler = logging.StreamHandler()
    file_handler = RotatingFileHandler(
        filename="../logs/server.log", maxBytes=1024 * 1024, backupCount=3
    )

    # add format to handlers
    stream_handler.setFormatter(log_format)
    file_handler.setFormatter(log_format)

    # add handlers to logger
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger

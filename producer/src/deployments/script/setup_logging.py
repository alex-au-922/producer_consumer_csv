import logging
from logging.handlers import TimedRotatingFileHandler
from .config import LoggingConfig
import pathlib


def setup_logging() -> None:
    LOG_LEVEL_INT = getattr(logging, LoggingConfig.LOG_LEVEL.upper(), None)

    pathlib.Path(LoggingConfig.LOG_DIR).mkdir(parents=True, exist_ok=True)

    handlers: list[logging.Handler] = []

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter(
            LoggingConfig.LOG_FORMAT, datefmt=LoggingConfig.LOG_DATE_FORMAT
        )
    )
    stream_handler.setLevel(LoggingConfig.LOG_LEVEL)
    handlers.append(stream_handler)

    # if LOG_LEVEL_INT is not None and LOG_LEVEL_INT <= logging.INFO:
    info_handler = TimedRotatingFileHandler(
        filename=f"{LoggingConfig.LOG_DIR}/info.log",
        when=LoggingConfig.LOG_ROTATION,
        interval=1,
        backupCount=LoggingConfig.LOG_RETENTION,
    )
    info_handler.setFormatter(
        logging.Formatter(
            LoggingConfig.LOG_FORMAT, datefmt=LoggingConfig.LOG_DATE_FORMAT
        )
    )
    info_handler.setLevel(logging.INFO)
    handlers.append(info_handler)

    # if LOG_LEVEL_INT is not None and LOG_LEVEL_INT <= logging.WARNING:
    warning_handler = TimedRotatingFileHandler(
        filename=f"{LoggingConfig.LOG_DIR}/warning.log",
        when=LoggingConfig.LOG_ROTATION,
        interval=1,
        backupCount=LoggingConfig.LOG_RETENTION,
    )
    warning_handler.setFormatter(
        logging.Formatter(
            LoggingConfig.LOG_FORMAT, datefmt=LoggingConfig.LOG_DATE_FORMAT
        )
    )
    warning_handler.setLevel(logging.WARNING)
    handlers.append(warning_handler)

    # if LOG_LEVEL_INT is not None and LOG_LEVEL_INT <= logging.ERROR:
    error_handler = TimedRotatingFileHandler(
        filename=f"{LoggingConfig.LOG_DIR}/error.log",
        when=LoggingConfig.LOG_ROTATION,
        interval=1,
        backupCount=LoggingConfig.LOG_RETENTION,
    )
    error_handler.setFormatter(
        logging.Formatter(
            LoggingConfig.LOG_FORMAT, datefmt=LoggingConfig.LOG_DATE_FORMAT
        )
    )
    error_handler.setLevel(logging.ERROR)
    handlers.append(error_handler)

    root_logger = logging.getLogger()
    root_logger.setLevel(LoggingConfig.LOG_LEVEL)
    root_logger.handlers = handlers

import logging
from logging.handlers import TimedRotatingFileHandler
from .config import LoggingConfig
import pathlib


def setup_logging() -> None:
    pathlib.Path(LoggingConfig.LOG_DIR).absolute().mkdir(parents=True, exist_ok=True)

    (pathlib.Path(LoggingConfig.LOG_DIR).absolute() / "info.log").touch()
    (pathlib.Path(LoggingConfig.LOG_DIR).absolute() / "warning.log").touch()
    (pathlib.Path(LoggingConfig.LOG_DIR).absolute() / "error.log").touch()

    handlers: list[logging.Handler] = []

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter(
            LoggingConfig.LOG_FORMAT, datefmt=LoggingConfig.LOG_DATE_FORMAT
        )
    )
    stream_handler.setLevel(LoggingConfig.LOG_LEVEL)
    handlers.append(stream_handler)

    info_handler = TimedRotatingFileHandler(
        filename=str(pathlib.Path(LoggingConfig.LOG_DIR).absolute() / "info.log"),
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

    warning_handler = TimedRotatingFileHandler(
        filename=str(pathlib.Path(LoggingConfig.LOG_DIR).absolute() / "warning.log"),
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

    error_handler = TimedRotatingFileHandler(
        filename=str(pathlib.Path(LoggingConfig.LOG_DIR).absolute() / "error.log"),
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

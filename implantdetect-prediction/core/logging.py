import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logging():
    os.makedirs("logs", exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(levelname)s | %(asctime)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler])


def get_logger(name: str = __name__) -> logging.Logger:
    return logging.getLogger(name)

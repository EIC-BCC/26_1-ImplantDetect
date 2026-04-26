import os
import logging


def setup_logging():
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s | %(asctime)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )


def get_logger(name: str = __name__):
    return logging.getLogger(name)

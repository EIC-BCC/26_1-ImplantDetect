import os
import logging

def setup_logging():
    """
    Configura o logging para a aplicação.
    """
    
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
    
    logger = logging.getLogger(__name__)
    return logger

def get_logger(name: str = __name__):
    """
    Retorna uma instância de logger.
    """

    return logging.getLogger(name)

setup_logging()
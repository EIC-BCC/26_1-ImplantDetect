"""Gerenciamento de filas utilizando o Greenstalk (Beanstalkd) ou fila em memória"""

import json
import logging
import queue
import socket
from contextlib import contextmanager
import greenstalk

from core.configuration import settings

# Configura o logger
logger = logging.getLogger(__name__)

def get_beanstalk_connection():
    """Verifica se o Beanstalkd está acessível"""
    try:
        original_level = logger.getEffectiveLevel()
        logger.setLevel(logging.INFO)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        
        logger.info(f"Tentando conectar ao Beanstalkd em {settings.BEANSTALK_HOST}:{settings.BEANSTALK_PORT}")
        
        result = sock.connect_ex((settings.BEANSTALK_HOST, settings.BEANSTALK_PORT))
        sock.close()
        
        if result == 0:
            logger.info(f"Beanstalkd está acessível em {settings.BEANSTALK_HOST}:{settings.BEANSTALK_PORT}")
            logger.setLevel(original_level)
            return True
        else:
            error_message = f"Não foi possível conectar ao Beanstalkd em {settings.BEANSTALK_HOST}:{settings.BEANSTALK_PORT}. Código de erro: {result}"
            logger.warning(error_message)
            logger.setLevel(original_level)
            return False
    except Exception as e:
        logger.exception(f"Erro ao verificar conexão com Beanstalkd em {settings.BEANSTALK_HOST}:{settings.BEANSTALK_PORT}:")
        logger.setLevel(original_level)
        return False

class QueueConnection:
    """Wrapper para unificar o acesso à fila, seja Beanstalk ou memória"""
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type == greenstalk.TimedOutError:
            # Ignora o erro de timeout, é esperado
            return True
        
        if hasattr(self.connection, 'close'):
            try:
                self.connection.close()
            except Exception as e:
                logger.exception("Erro ao fechar conexão:")
        return False

def get_queue_connection():
    """Retorna uma conexão com a fila (Beanstalk ou memória)"""

    try:
        max_retries = 3
        for attempt in range(max_retries):
            if attempt > 0:
                logger.info(f"Tentativa {attempt + 1} de {max_retries} de conectar ao Beanstalkd")
                
            if get_beanstalk_connection():
                try:
                    # Tenta criar o cliente Beanstalk
                    client = greenstalk.Client(
                        address=(settings.BEANSTALK_HOST, settings.BEANSTALK_PORT),
                        watch=[settings.BEANSTALK_TUBE],
                        use=settings.BEANSTALK_TUBE
                    )
                    
                    # Testa a conexão com um comando simples
                    stats = client.stats()
                    jobs_ready = stats.get('current-jobs-ready', 0)
                    logger.info(f"Conectado ao Beanstalkd. Jobs na fila: {jobs_ready}")
                    
                    return QueueConnection(client)
                except Exception as e:
                    logger.warning(f"Falha ao criar cliente Beanstalkd na tentativa {attempt + 1}: {str(e)}")
                    if attempt == max_retries - 1:
                        raise  # Re-lança a exceção na última tentativa
            elif attempt == max_retries - 1:
                logger.warning("Todas as tentativas de conexão com Beanstalkd falharam")
                break
                
    except Exception as e:
        logger.exception(f"Erro ao conectar ao Beanstalkd ({settings.BEANSTALK_HOST}:{settings.BEANSTALK_PORT}):")
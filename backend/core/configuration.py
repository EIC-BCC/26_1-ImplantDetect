"""
Configurações do aplicativo.

Esta classe contém as configurações necessárias para o funcionamento do aplicativo,
como a chave secreta, o algoritmo de criptografia e o tempo de expiração do token de acesso.
As configurações são carregadas a partir de variáveis de ambiente, com valores padrão definidos.
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Configurar o logger para usar níveis de log apropriados
logging.getLogger('core.beanstalk').setLevel(logging.WARNING)  # Reduz logs de conexão
logging.getLogger('greenstalk').setLevel(logging.WARNING)  # Reduz logs do cliente beanstalkd

class Settings:
    # Configuração de segurança (JWT)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_default_secret_key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    
    # Configurações de upload de imagens
    IMAGE_REPOSITORY: str = os.getenv("IMAGE_REPOSITORY", "./uploads")
    IMAGE_MAXIMUM_SIZE: int = int(os.getenv("IMAGE_MAXIMUM_SIZE", 50 * 1024 * 1024))  # 50 MB
    IMAGE_SUPPORTED_FORMATS: list = os.getenv("IMAGE_SUPPORTED_FORMATS", "JPG,JPEG,PNG").split(",")
    
    # Configurações do banco de dados
    DATABASE_URL: str = os.getenv("DATABASE_URL", None)
    SQL_ECHO: bool = os.getenv("SQL_ECHO", "false").lower() == "true"
    
    # Configurações do Beanstalk
    BEANSTALK_HOST: str = os.getenv("BEANSTALK_HOST", "localhost")
    BEANSTALK_PORT: int = int(os.getenv("BEANSTALK_PORT", 11300))
    BEANSTALK_TUBE: str = os.getenv("BEANSTALK_TUBE", "implantdetect")
    
    # Configurações do worker
    RUN_WORKER_IN_PROCESS: bool = os.getenv("RUN_WORKER_IN_PROCESS", "false").lower() == "true"
    WORKER_THREADS: int = int(os.getenv("WORKER_THREADS", 1))
    MAX_CONCURRENT_JOBS: int = int(os.getenv("MAX_CONCURRENT_JOBS", 1))

settings = Settings()

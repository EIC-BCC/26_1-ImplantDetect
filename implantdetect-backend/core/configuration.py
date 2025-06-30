import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # Configuração de segurança (JWT)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_default_secret_key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    
    # Configurações de upload de imagens
    IMAGE_REPOSITORY: str = os.getenv("IMAGE_REPOSITORY", "./uploads")
    IMAGE_MAXIMUM_SIZE: int = int(os.getenv("IMAGE_MAXIMUM_SIZE", 50 * 1024 * 1024))  # 50 MB
    IMAGE_SUPPORTED_FORMATS: list = os.getenv("IMAGE_SUPPORTED_FORMATS", "JPG,JPEG,PNG").split(",")
    
    # Configurações do banco de dados
    DATABASE_URL: str = os.getenv("DATABASE_URL", None) # type: ignore
    SQL_ECHO: bool = os.getenv("SQL_ECHO", "false").lower() == "true"

settings = Settings()
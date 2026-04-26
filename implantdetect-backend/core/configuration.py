import os
from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    raise ValueError(f"Required environment variable '{name}' is not set.")


class Settings:
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    UPLOAD_FILE_PATH: str = os.getenv("UPLOAD_FILE_PATH", "./uploads")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_default_secret_key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    IMAGE_REPOSITORY: str = os.getenv("IMAGE_REPOSITORY", "./uploads")
    IMAGE_MAXIMUM_SIZE: int = int(os.getenv("IMAGE_MAXIMUM_SIZE", 50 * 1024 * 1024))
    IMAGE_SUPPORTED_FORMATS: list = os.getenv(
        "IMAGE_SUPPORTED_FORMATS", "JPG,JPEG,PNG"
    ).split(",")

    DATABASE_URL: str = os.getenv("DATABASE_URL") or _require("DATABASE_URL")
    SQL_ECHO: bool = os.getenv("SQL_ECHO", "false").lower() == "true"

    YOLO_MODEL_PATH: str = os.getenv("YOLO_MODEL_PATH", "yolo11m-obb.pt")
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


settings = Settings()

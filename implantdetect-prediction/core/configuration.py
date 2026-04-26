import os
from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    raise ValueError(f"Required environment variable '{name}' is not set.")


class Settings:
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    UPLOAD_FILE_PATH: str = os.getenv("UPLOAD_FILE_PATH", "./uploads")

    DATABASE_URL: str = os.getenv("DATABASE_URL") or _require("DATABASE_URL")
    SQL_ECHO: bool = os.getenv("SQL_ECHO", "false").lower() == "true"

    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
    YOLO_MODEL_PATH: str = os.getenv("YOLO_MODEL_PATH", "yolo11m-obb.pt")


settings = Settings()

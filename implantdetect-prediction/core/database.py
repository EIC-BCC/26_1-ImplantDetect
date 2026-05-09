from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core.configuration import settings
from core.logging import get_logger

logger = get_logger(__name__)

async_engine = create_async_engine(
    settings.DATABASE_URL, echo=settings.SQL_ECHO, future=True
)

async_session_factory = async_sessionmaker(bind=async_engine, expire_on_commit=False)

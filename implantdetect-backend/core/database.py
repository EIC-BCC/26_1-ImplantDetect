from sqlalchemy import text
from fastapi import HTTPException, status
from sqlalchemy.schema import CreateSchema
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from core.logging import get_logger
from models.entities.base import Base
from core.configuration import settings

logger = get_logger(__name__)

async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.SQL_ECHO,
    future=True
)

async_session_factory = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False
)

async def get_async_db():
    """
    Fornece uma sessão de banco de dados assíncrona.
    """
    
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        
        except HTTPException:
            await session.rollback()
            raise
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Database error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno do banco de dados: {str(e)}"
            )
            
        finally:
            await session.close()

async def create_tables():
    """
    Cria as tabelas do banco de dados.
    """
    
    try:
        async with async_engine.begin() as conn:
            schemas = await conn.run_sync(lambda sync_conn: sync_conn.dialect.get_schema_names(sync_conn))
            if 'public' not in schemas:
                await conn.execute(CreateSchema('public'))
            
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("Tabelas do banco de dados criadas com sucesso")
    
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {str(e)}", exc_info=False)

async def database_health_check():
    """
    Verifica se o banco de dados está disponível.
    """
    
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
            logger.info("Banco de dados assíncrono está acessível")
            return "available"
        
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados assíncrono: {str(e)}", exc_info=True)
        return "unavailable"
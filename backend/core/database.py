"""Banco de dados PostgreSQL utilizando SQLAlchemy assíncrono"""

import logging
import traceback
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException, status
from sqlalchemy.schema import CreateSchema
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from core.configuration import settings
from models.entities.base import Base

# Criar a engine assíncrona
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.SQL_ECHO,
    future=True
)

# Criar o sessionmaker assíncrono
async_session_factory = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_async_db():
    """Fornece uma sessão de banco de dados assíncrona"""
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logging.error(f"Database error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do banco de dados: {str(e)}"
        )
    finally:
        await session.close()

async def create_tables():
    """Cria as tabelas do banco de dados de forma assíncrona"""
    try:
        async with async_engine.begin() as conn:
            # Verificar e criar o schema público se necessário
            schemas = await conn.run_sync(lambda sync_conn: sync_conn.dialect.get_schema_names(sync_conn))
            if 'public' not in schemas:
                await conn.execute(CreateSchema('public'))
            
            # Criar todas as tabelas
            await conn.run_sync(Base.metadata.create_all)
            
        logging.info("Tabelas do banco de dados criadas com sucesso")
    except Exception as e:
        logging.error(f"Erro ao criar tabelas: {str(e)}", exc_info=True)
        raise
        
async def database_health_check():
    """Verifica a saúde do banco de dados assíncrono"""
    try:
        async with async_session_factory() as session:
            await session.execute("SELECT 1")
            logging.info("Banco de dados assíncrono está acessível")
            return "available"
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco de dados assíncrono: {str(e)}", exc_info=True)
        return "unavailable"
"""
Script para execução do worker que processa imagens na fila do Beanstalk.
Execute este script em um processo separado do servidor da API.
"""
import sys
import json
import logging
import os
import asyncio
import greenstalk
from pathlib import Path
from datetime import datetime

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.semaphore import semaphore
from core.beanstalk import get_queue_connection
from core.database import async_session_factory
from daos.queue_dao import QueueDao
from enums.process_status import ProcessStatus
from core.configuration import settings

# Criar diretório de logs se não existir
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/worker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info(f"Tentando usar Beanstalkd em {settings.BEANSTALK_HOST}:{settings.BEANSTALK_PORT}")

async def process_image(image_id: int, queue_id: int) -> bool:
    """
    Processa uma imagem e atualiza seu status na fila.
    Retorna True se o processamento foi bem sucedido, False caso contrário.
    """
    try:
        logger.info(f"Processando imagem {image_id} (Queue ID: {queue_id})...")
        # Simular processamento
        await asyncio.sleep(10)
        logger.info(f"Imagem {image_id} (Queue ID: {queue_id}) processada com sucesso!")
        return True
    except Exception as e:
        logger.exception(f"Erro ao processar imagem {image_id}:")
        return False

async def process_job(payload: dict):
    """
    Processa um job da fila.
    """
    queue_id = payload.get('queue_id')
    image_id = payload.get('image_id')

    try:
        logger.info(f"Processando imagem {image_id} (Queue ID: {queue_id})...")

        async with async_session_factory() as db:
            queue_dao = QueueDao(db)

            # Atualizar status para processando
            await queue_dao.update_status(queue_id, ProcessStatus.RUNNING)

            # Processar a imagem
            success = await process_image(image_id, queue_id)

            # Atualizar status final
            if success:
                await queue_dao.update_status(queue_id, ProcessStatus.FINISHED)
                logger.info(f"Imagem {image_id} (Queue ID: {queue_id}) processada com sucesso!")
            else:
                await queue_dao.update_status(queue_id, ProcessStatus.ERROR)
                logger.error(f"Falha ao processar imagem {image_id}")

            await db.commit()

    except Exception as e:
        logger.exception(f"Erro ao processar job {queue_id}:")
        async with async_session_factory() as db:
            queue_dao = QueueDao(db)
            await queue_dao.update_status(queue_id, ProcessStatus.ERROR)
            await db.commit()
        raise

async def process_queue():
    """Processa trabalhos da fila"""
    while True:
        try:
            with get_queue_connection() as queue:
                try:
                    job = queue.reserve(timeout=5)
                    if job is None:
                        await asyncio.sleep(1)
                        continue

                    try:
                        payload = json.loads(job.body)
                        logger.info(f"Job recebido: Imagem ID {payload.get('image_id')}, Queue ID {payload.get('queue_id')}")
                        logger.info(f"Processando job: {payload}")

                        # Processa o trabalho
                        await process_job(payload)

                        # Remove o trabalho da fila após processamento bem-sucedido
                        queue.delete(job)

                    except Exception as e:
                        logger.exception(f"Erro ao processar job:")
                        queue.release(job)  # Reenvia o job para a fila

                    finally:
                        semaphore.release()
                        logger.info("Semáforo liberado")

                except greenstalk.TimedOutError:
                    await asyncio.sleep(1)
                    continue
                except Exception as e:
                    logger.exception("Erro ao processar fila:")
                    await asyncio.sleep(5)

        except Exception as e:
            logger.exception("Erro inesperado no worker:")
            await asyncio.sleep(5)

async def main():
    """Função principal do worker"""
    logger.info("Iniciando worker...")
    try:
        await process_queue()
    except KeyboardInterrupt:
        logger.info("Worker interrompido pelo usuário")
    except Exception as e:
        logger.exception("Erro fatal no worker:")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
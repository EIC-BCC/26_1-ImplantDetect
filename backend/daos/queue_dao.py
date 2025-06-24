import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.entities.queue import Queue
from enums.process_status import ProcessStatus

class QueueDao:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_images_in_queue(self):
        """
        Retorna todas as imagens na fila com status PENDING.
        """
        result = await self.db.execute(select(Queue).filter(Queue.id_status == ProcessStatus.PENDING))
        return list(result.scalars().all())

    async def get_images_in_progress(self):
        """
        Retorna todas as imagens na fila com status RUNNING.
        """
        result = await self.db.execute(select(Queue).filter(Queue.id_status == ProcessStatus.RUNNING))
        return list(result.scalars().all())

    async def get_images_finished(self):
        """
        Retorna todas as imagens na fila com status FINISHED.
        """
        result = await self.db.execute(select(Queue).filter(Queue.id_status == ProcessStatus.FINISHED))
        return list(result.scalars().all())

    async def get_images_error(self):
        """
        Retorna todas as imagens na fila com status ERROR.
        """
        result = await self.db.execute(select(Queue).filter(Queue.id_status == ProcessStatus.ERROR))
        return list(result.scalars().all())

    async def get_queue_by_id(self, queue_id: int):
        """
        Retorna uma fila pelo ID.
        """
        result = await self.db.execute(select(Queue).filter(Queue.id == queue_id))
        return result.scalars().first()

    async def add_image_to_queue(self, queue: Queue):
        """
        Adiciona uma nova imagem à fila.
        """
        self.db.add(queue)
        await self.db.commit()
        await self.db.refresh(queue)
        return queue

    async def remove_image_from_queue(self, queue_id: int):
        """
        Remove uma imagem da fila pelo ID.
        Ao invés de deletar, a imagem é marcada como CANCELED.
        """
        queue = await self.get_queue_by_id(queue_id)
        if queue:
            queue.id_status = ProcessStatus.CANCELED
            self.db.add(queue)
            await self.db.commit()
            return queue
        return None

    async def update_image_in_queue(self, queue_id: int, updated_data: dict):
        """
        Atualiza os dados de uma imagem na fila pelo ID.
        """
        queue = await self.get_queue_by_id(queue_id)
        if queue:
            for key, value in updated_data.items():
                setattr(queue, key, value)
            await self.db.commit()
            await self.db.refresh(queue)
            return queue
        return None

    async def get_all_images_in_queue(self):
        """
        Retorna todas as imagens na fila.
        """
        result = await self.db.execute(select(Queue))
        return list(result.scalars().all())

    async def update_status(self, queue_id: int, status: ProcessStatus) -> bool:
        """
        Atualiza o status de uma fila.
        """
        try:
            queue = await self.get_queue_by_id(queue_id)
            if not queue:
                logging.error(f"Fila não encontrada: {queue_id}")
                return False
            
            queue.status = status
            
            # Update timestamps based on status
            if status == ProcessStatus.FINISHED:
                queue.finished_at = datetime.now()
            elif status == ProcessStatus.RUNNING:
                queue.started_at = datetime.now()

            await self.db.commit()
            logging.info(f"Status da fila {queue_id} atualizado para {status}")
            return True
        except Exception as e:
            logging.exception(f"Erro ao atualizar status da fila {queue_id}:")
            await self.db.rollback()
            return False

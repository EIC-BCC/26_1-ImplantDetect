"""
Service para gerenciamento da fila de processamento de imagens
"""
import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from daos.queue_dao import QueueDao
from models.entities.queue import Queue
from models.dtos.queue_dto import QueueRequest, QueueResponse
from enums.process_status import ProcessStatus
from workers.beanstalk_worker import add_job_to_queue, get_job_stats, delete_job

class QueueService:
    def __init__(self, db: Session):
        self.dao = QueueDao(db)
        
    async def add_to_queue(self, request: QueueRequest):
        """
        Adiciona uma tarefa à fila de processamento
        1. Cria um registro no banco para rastreamento
        2. Adiciona a tarefa ao Beanstalk para processamento assíncrono
        """
        try:
            queue_entry = Queue(
                image_id=request.image_id,
                id_status=ProcessStatus.PENDING,
                user_id=request.user_id
            )
            
            db_entry = await self.dao.add_image_to_queue(queue_entry)
            
            payload = {
                "queue_id": db_entry.id,
                "image_id": db_entry.image_id,
                "user_id": db_entry.user_id
            }
            
            job_id = add_job_to_queue(payload)
            
            if job_id is None:
                await self.dao.update_status(db_entry.id, ProcessStatus.ERROR.value)  # Use .value
                error_msg = "Não foi possível adicionar a imagem à fila de processamento"
                logging.error(f"{error_msg} (ID: {db_entry.id})")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_msg
                )
                
            logging.info(f"Imagem {db_entry.id} adicionada à fila com job_id {job_id}")
            return db_entry.id
            
        except HTTPException:
            raise
        except Exception as e:
            logging.exception("Erro ao adicionar imagem à fila:")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao adicionar imagem à fila: {str(e)}"
            )
            
    async def get_queue_status(self, queue_id: int) -> QueueResponse:
        """
        Retorna o status de uma tarefa na fila
        """
        try:
            queue = await self.dao.get_queue_by_id(queue_id)
            if not queue:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Imagem não encontrada na fila (ID: {queue_id})"
                )
            
            queue_status = ProcessStatus(queue.id_status)
            if queue_status == ProcessStatus.PENDING:
                stats = get_job_stats(queue_id)
                if stats:
                    position = stats.get('id', 0)
                else:
                    position = 0
            else:
                position = 0
            
            return QueueResponse.from_orm(queue)
            
        except HTTPException:
            raise
        except Exception as e:
            logging.exception(f"Erro ao obter status da fila {queue_id}:")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao obter status da fila: {str(e)}"
            )
            
    async def cancel_processing(self, queue_id: int) -> bool:
        """
        Cancela o processamento de uma imagem na fila
        """
        try:
            queue = await self.dao.get_queue_by_id(queue_id)
            if not queue:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Imagem não encontrada na fila (ID: {queue_id})"
                )
            
            queue_status = ProcessStatus(queue.id_status)
            if queue_status in [ProcessStatus.COMPLETED, ProcessStatus.ERROR]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Não é possível cancelar uma tarefa que já foi concluída ou falhou (ID: {queue_id})"
                )
            
            if delete_job(queue_id):
                await self.dao.update_status(queue_id, ProcessStatus.CANCELED)
                return True
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Não foi possível cancelar o processamento da imagem (ID: {queue_id})"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logging.exception(f"Erro ao cancelar processamento da fila {queue_id}:")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao cancelar processamento: {str(e)}"
            )
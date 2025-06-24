from fastapi import APIRouter, Depends, HTTPException
from core.database import get_async_db
from services.queue_service import QueueService
from models.dtos.result_dto import Result
from models.dtos.queue_dto import QueueRequest
from core.security import get_current_user

router = APIRouter()

@router.post("/submit", response_model=Result)
async def add_to_queue(request: QueueRequest, db=Depends(get_async_db), user=Depends(get_current_user)):
    """
    Adiciona uma imagem à fila de processamento
    """
    queue_service = QueueService(db)
    try:
        result = await queue_service.add_to_queue(request)
        return Result.ok(message="Imagem adicionada à fila com sucesso", data=result.model_dump())
    except Exception as e:
        return Result.error(message=str(e))

@router.get("/pending", response_model=Result)
async def get_pending_queue(db=Depends(get_async_db), user=Depends(get_current_user)):
    """
    Retorna todas as imagens pendentes na fila
    """
    queue_service = QueueService(db)
    try:
        queues = await queue_service.get_all_pending()
        return Result.ok(data={"queues": [q.model_dump() for q in queues]})
    except Exception as e:
        return Result.error(message=str(e))

@router.get("/processing", response_model=Result)
async def get_processing_queue(db=Depends(get_async_db), user=Depends(get_current_user)):
    """
    Retorna todas as imagens em processamento
    """
    queue_service = QueueService(db)
    try:
        queues = await queue_service.get_all_in_progress()
        return Result.ok(data={"queues": [q.model_dump() for q in queues]})
    except Exception as e:
        return Result.error(message=str(e))

@router.get("/completed", response_model=Result)
async def get_completed_queue(db=Depends(get_async_db), user=Depends(get_current_user)):
    """
    Retorna todas as imagens processadas
    """
    queue_service = QueueService(db)
    try:
        queues = await queue_service.get_all_finished()
        return Result.ok(data={"queues": [q.model_dump() for q in queues]})
    except Exception as e:
        return Result.error(message=str(e))

@router.get("/errors", response_model=Result)
async def get_error_queue(db=Depends(get_async_db), user=Depends(get_current_user)):
    """
    Retorna todas as imagens com erro
    """
    queue_service = QueueService(db)
    try:
        queues = await queue_service.get_all_with_error()
        return Result.ok(data={"queues": [q.model_dump() for q in queues]})
    except Exception as e:
        return Result.error(message=str(e))

@router.get("/{queue_id}", response_model=Result)
async def get_queue_status(queue_id: int, db=Depends(get_async_db), user=Depends(get_current_user)):
    """
    Retorna o status atual de uma imagem na fila
    """
    queue_service = QueueService(db)
    try:
        queue = await queue_service.get_status(queue_id)
        return Result.ok(data=queue.model_dump())
    except Exception as e:
        return Result.error(message=str(e))

@router.get("/{queue_id}/position", response_model=Result)
async def get_queue_position(queue_id: int, db=Depends(get_async_db), user=Depends(get_current_user)):
    """
    Retorna a posição na fila de processamento
    """
    queue_service = QueueService(db)
    try:
        position = await queue_service.get_queue_position(queue_id)
        return Result.ok(data=position)
    except Exception as e:
        return Result.error(message=str(e))

@router.delete("/{queue_id}", response_model=Result)
async def cancel_processing(queue_id: int, db=Depends(get_async_db), user=Depends(get_current_user)):
    """
    Cancela o processamento de uma imagem
    """
    queue_service = QueueService(db)
    try:
        result = await queue_service.cancel_processing(queue_id)
        return Result.ok(message=f"Processamento da imagem {queue_id} cancelado com sucesso")
    except Exception as e:
        return Result.error(message=str(e))

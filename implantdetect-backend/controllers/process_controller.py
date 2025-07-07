from fastapi import APIRouter, Depends

from core.database import get_async_db
from models.dtos.result_dto import Result
from core.security import get_current_user
from services.process_service import ProcessService

router = APIRouter()

@router.get("/process/{process_id}", response_model=Result)
async def get_process(process_id: int, db=Depends(get_async_db), user=Depends(get_current_user)):
    """
    Busca um processo específico pelo ID.
    """
    process_service = ProcessService(db)
    process = await process_service.get_process(process_id)
    return Result.ok(data={"process": process.model_dump()})

@router.get("/user/processes", response_model=Result)
async def get_user_processes(db=Depends(get_async_db), user=Depends(get_current_user)):
    """
    Busca todos os processos do usuário autenticado.
    """
    # Extrai o ID do usuário do token JWT
    user_id = int(user["sub"])
    process_service = ProcessService(db)
    processes = await process_service.get_all_processes_by_user(user_id)
    return Result.ok(data={"processes": [process.model_dump() for process in processes]})

@router.get("/process/{process_id}/results", response_model=Result)
async def get_process_results(process_id: int, db=Depends(get_async_db), user=Depends(get_current_user)):
    """
    Busca os resultados de um processo específico.
    """
    process_service = ProcessService(db)
    results = await process_service.get_results_by_process_id(process_id)
    return Result.ok(data={"results": [result.model_dump() for result in results]})

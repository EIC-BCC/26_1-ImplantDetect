from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from core.security import get_current_user, JWTPayload
from implantdetect_shared.models.dtos.result_dto import Result
from services.process_service import ProcessService

router = APIRouter()


@router.get("/user/processes", response_model=Result)
async def get_user_processes(
    db: AsyncSession = Depends(get_async_db),
    user: JWTPayload = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    user_id = int(user["sub"])
    process_service = ProcessService(db)
    processes = await process_service.get_all_processes_by_user(
        user_id, limit=page_size, offset=(page - 1) * page_size
    )
    return Result.ok(
        data={"processes": [process.model_dump() for process in processes]}
    )


@router.get("/{process_id}", response_model=Result)
async def get_process(
    process_id: int,
    db: AsyncSession = Depends(get_async_db),
    user: JWTPayload = Depends(get_current_user),
):
    user_id = int(user["sub"])
    process_service = ProcessService(db)
    process = await process_service.get_process(process_id)

    if process.user_id != user_id and user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado."
        )

    return Result.ok(data={"process": process.model_dump()})


@router.get("/{process_id}/results", response_model=Result)
async def get_process_results(
    process_id: int,
    db: AsyncSession = Depends(get_async_db),
    user: JWTPayload = Depends(get_current_user),
):
    user_id = int(user["sub"])
    process_service = ProcessService(db)

    # Verificar ownership antes de retornar resultados
    process = await process_service.get_process(process_id)
    if process.user_id != user_id and user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado."
        )

    results = await process_service.get_results_by_process_id(process_id)
    return Result.ok(data={"results": [result.model_dump() for result in results]})

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from core.deps import require_role
from core.security import JWTPayload
from implantdetect_shared.daos.user_dao import UserDao
from implantdetect_shared.daos.process_dao import ProcessDao
from implantdetect_shared.models.dtos.result_dto import Result
from implantdetect_shared.models.dtos.user_dto import (
    UserResponse,
    SetRoleRequest,
    SetActiveRequest,
)
from services.process_service import ProcessService

router = APIRouter()

_admin_dep = require_role("admin")


@router.get("/users", response_model=Result)
async def list_all_users(
    db: AsyncSession = Depends(get_async_db),
    _: JWTPayload = _admin_dep,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    dao = UserDao(db)
    users = await dao.get_all_users(limit=page_size, offset=(page - 1) * page_size)
    return Result.ok(
        data={"users": [UserResponse.from_orm(u).model_dump() for u in users]}
    )


@router.patch("/users/{user_id}/role", response_model=Result)
async def set_user_role(
    user_id: int,
    body: SetRoleRequest,
    db: AsyncSession = Depends(get_async_db),
    _: JWTPayload = _admin_dep,
):
    dao = UserDao(db)
    target = await dao.get_user_by_id(user_id)
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado."
        )
    target.role = body.role
    db.add(target)
    await db.commit()
    await db.refresh(target)
    return Result.ok(
        message="Papel atualizado.", data=UserResponse.from_orm(target).model_dump()
    )


@router.patch("/users/{user_id}/active", response_model=Result)
async def set_user_active(
    user_id: int,
    body: SetActiveRequest,
    db: AsyncSession = Depends(get_async_db),
    _: JWTPayload = _admin_dep,
):
    dao = UserDao(db)
    target = await dao.get_user_by_id(user_id)
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado."
        )
    target.active = 1 if body.active else 0
    db.add(target)
    await db.commit()
    await db.refresh(target)
    return Result.ok(
        message="Status atualizado.", data=UserResponse.from_orm(target).model_dump()
    )


@router.get("/processes", response_model=Result)
async def list_all_processes(
    db: AsyncSession = Depends(get_async_db),
    _: JWTPayload = _admin_dep,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    dao = ProcessDao(db)
    process_service = ProcessService(db)
    processes = await dao.get_all_processes(
        limit=page_size, offset=(page - 1) * page_size
    )
    result = [
        {
            "process_id": p.id,
            "user_id": p.user_id,
            "image_id": p.image_id,
            "status": p.status,
            "status_name": process_service._get_status_name(getattr(p, "status", 0)),
            "created_at": str(p.created_at),
            "updated_at": str(p.updated_at),
        }
        for p in processes
    ]
    return Result.ok(data={"processes": result})

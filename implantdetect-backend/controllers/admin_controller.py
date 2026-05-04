from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from core.security import get_current_user, JWTPayload
from implantdetect_shared.daos.user_dao import UserDao
from implantdetect_shared.daos.process_dao import ProcessDao
from implantdetect_shared.models.dtos.result_dto import Result
from implantdetect_shared.models.dtos.user_dto import UserResponse
from services.process_service import ProcessService

router = APIRouter()


def _require_admin(user: JWTPayload) -> None:
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores.",
        )


@router.get("/users", response_model=Result)
async def list_all_users(
    db: AsyncSession = Depends(get_async_db),
    user: JWTPayload = Depends(get_current_user),
):
    _require_admin(user)
    dao = UserDao(db)
    users = await dao.get_all_users()
    return Result.ok(data={"users": [UserResponse.from_orm(u).model_dump() for u in users]})


@router.patch("/users/{user_id}/role", response_model=Result)
async def set_user_role(
    user_id: int,
    body: dict,
    db: AsyncSession = Depends(get_async_db),
    user: JWTPayload = Depends(get_current_user),
):
    _require_admin(user)
    role = body.get("role")
    if role not in ("user", "specialist", "admin"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Papel inválido."
        )
    dao = UserDao(db)
    target = await dao.get_user_by_id(user_id)
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado."
        )
    target.role = role
    db.add(target)
    await db.commit()
    await db.refresh(target)
    return Result.ok(
        message="Papel atualizado.", data=UserResponse.from_orm(target).model_dump()
    )


@router.patch("/users/{user_id}/active", response_model=Result)
async def set_user_active(
    user_id: int,
    body: dict,
    db: AsyncSession = Depends(get_async_db),
    user: JWTPayload = Depends(get_current_user),
):
    _require_admin(user)
    active = body.get("active")
    if not isinstance(active, bool):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campo 'active' deve ser booleano.",
        )
    dao = UserDao(db)
    target = await dao.get_user_by_id(user_id)
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado."
        )
    target.active = 1 if active else 0
    db.add(target)
    await db.commit()
    await db.refresh(target)
    return Result.ok(
        message="Status atualizado.", data=UserResponse.from_orm(target).model_dump()
    )


@router.get("/processes", response_model=Result)
async def list_all_processes(
    db: AsyncSession = Depends(get_async_db),
    user: JWTPayload = Depends(get_current_user),
):
    _require_admin(user)
    dao = ProcessDao(db)
    process_service = ProcessService(db)
    processes = await dao.get_all_processes()
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

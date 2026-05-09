from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from core.limiter import limiter
from core.security import get_current_user, JWTPayload
from implantdetect_shared.models.dtos.result_dto import Result
from services.user_service import UserService
from implantdetect_shared.models.dtos.user_dto import (
    UserTokenResponse,
    UserResponse,
    UserRegisterRequest,
    UserUpdateRequest,
)

router = APIRouter()


@router.post("/login", response_model=UserTokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_async_db),
):
    user_service = UserService(db)
    token = await user_service.authenticate_user(username, password)
    return token


@router.post("/register", response_model=Result)
@limiter.limit("10/minute")
async def register(
    request: Request,
    user: UserRegisterRequest,
    db: AsyncSession = Depends(get_async_db),
):
    user_service = UserService(db)
    new_user = await user_service.add_user(user)
    return Result.ok(
        message="Usuário registrado com sucesso.",
        data=UserResponse.from_orm(new_user).model_dump(),
    )


@router.post("/update", response_model=Result)
async def update_user(
    user: UserUpdateRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: JWTPayload = Depends(get_current_user),
):
    # user_id vem do JWT, não do body — previne IDOR
    user.user_id = int(current_user["sub"])
    user_service = UserService(db)
    updated_user = await user_service.update_user(user)
    return Result.ok(
        message="Usuário atualizado com sucesso.",
        data=UserResponse.from_orm(updated_user).model_dump(),
    )


@router.get("/me", response_model=Result)
async def get_me(
    db: AsyncSession = Depends(get_async_db),
    current_user: JWTPayload = Depends(get_current_user),
):
    user_service = UserService(db)
    user_data = await user_service.get_user(int(current_user["sub"]))
    return Result.ok(data=UserResponse.from_orm(user_data).model_dump())


@router.get("/get/{user_id}", response_model=Result)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: JWTPayload = Depends(get_current_user),
):
    requesting_id = int(current_user["sub"])
    is_admin = current_user.get("role") == "admin"
    if not is_admin and requesting_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado."
        )
    user_service = UserService(db)
    user_data = await user_service.get_user(user_id)
    return Result.ok(data=UserResponse.from_orm(user_data).model_dump())

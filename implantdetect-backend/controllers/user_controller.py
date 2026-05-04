from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
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
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_async_db),
):
    user_service = UserService(db)
    token = await user_service.authenticate_user(username, password)
    return token


@router.post("/register", response_model=Result)
async def register(user: UserRegisterRequest, db: AsyncSession = Depends(get_async_db)):
    user_service = UserService(db)
    new_user = await user_service.add_user(user)
    return Result.ok(
        message="Usuário registrado com sucesso.",
        data=UserResponse.from_orm(new_user).model_dump(),
    )


@router.post("/update", response_model=Result)
async def update_user(
    user: UserUpdateRequest, db: AsyncSession = Depends(get_async_db)
):
    user_service = UserService(db)
    updated_user = await user_service.update_user(user)
    return Result.ok(
        message="Usuário atualizado com sucesso.",
        data=UserResponse.from_orm(updated_user).model_dump(),
    )


@router.get("/get/{user_id}", response_model=Result)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    user: JWTPayload = Depends(get_current_user),
):
    user_service = UserService(db)
    user_data = await user_service.get_user(user_id)
    return Result.ok(data=UserResponse.from_orm(user_data).model_dump())

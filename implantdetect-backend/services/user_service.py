from datetime import timedelta
from typing import NoReturn
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import get_logger
from core.configuration import settings
from core.security import create_access_token, verify_password, hash_password
from implantdetect_shared.daos.user_dao import UserDao
from implantdetect_shared.models.dtos.user_dto import (
    UserUpdateRequest,
    UserRegisterRequest,
    UserTokenResponse,
)

logger = get_logger(__name__)


class UserService:
    def __init__(self, db: AsyncSession):
        self.dao = UserDao(db)

    async def _handle_user_not_found(self) -> NoReturn:
        logger.error("Usuário não encontrado.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado."
        )

    async def add_user(self, user_data: UserRegisterRequest):
        existing_user = await self.dao.get_user_by_username_or_email(
            user_data.username
        ) or await self.dao.get_user_by_username_or_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome de usuário ou email já cadastrado.",
            )

        user = await self.dao.add_user(user_data, hash_password(user_data.password))

        logger.info(f"Usuário {user.username} ({user.email}) criado com sucesso.")
        return user

    async def authenticate_user(self, identifier: str, password: str):
        user = await self.dao.get_user_by_username_or_email(identifier)

        if not user:
            await self._handle_user_not_found()

        if not verify_password(password, str(user.hashed_password)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas.",
            )

        access_token = create_access_token(
            data={"sub": str(user.id), "role": getattr(user, "role", "user")},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        logger.info(f"Usuário {user.username} ({user.email}) autenticado com sucesso.")
        return UserTokenResponse.from_token(access_token, user.id, user.username, getattr(user, "role", "user"))

    async def get_user(self, user_id: int):
        user = await self.dao.get_user_by_id(user_id)

        if not user:
            await self._handle_user_not_found()

        logger.info(
            f"Dados do usuário {user.username} ({user.email}) recuperados com sucesso."
        )
        return user

    async def update_user(self, updated_user_data: UserUpdateRequest):
        user = await self.dao.update_user(updated_user_data, hash_password)

        if not user:
            await self._handle_user_not_found()

        logger.info(
            f"Dados do usuário {user.username} ({user.email}) atualizados com sucesso."
        )
        return user

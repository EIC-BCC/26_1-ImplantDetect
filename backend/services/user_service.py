from daos.user_dao import UserDao
from core.security import create_access_token, verify_password
from models.dtos.user_dto import UserUpdateRequest, UserRegisterRequest, UserTokenResponse
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.configuration import settings
from datetime import timedelta
import logging

class UserService:
    def __init__(self, db: AsyncSession):
        self.dao = UserDao(db)

    async def add_user(self, user_data: UserRegisterRequest):
        existing_user = await self.dao.get_user_by_username_or_email(user_data.username) or \
                       await self.dao.get_user_by_username_or_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        user = await self.dao.add_user(user_data)
        logging.info(f"Usuário {user.username} ({user.email}) criado com sucesso.")
        return user

    async def authenticate_user(self, identifier: str, password: str):
        user = await self.dao.get_user_by_username_or_email(identifier)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        logging.info(f"Usuário {user.username} ({user.email}) autenticado com sucesso.")
        return UserTokenResponse.from_token(access_token)

    async def get_user(self, user_id: int):
        user = await self.dao.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        logging.info(f"Dados do usuário {user.username} ({user.email}) recuperados com sucesso.")
        return user

    async def update_user(self, updated_user_data: UserUpdateRequest):
        user = await self.dao.update_user(updated_user_data)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        logging.info(f"Dados do usuário {user.username} ({user.email}) atualizados com sucesso.")
        return user

    async def remove_user(self, user_id: int):
        user = await self.dao.remove_user(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        logging.info(f"Usuário {user.username} ({user.email}) removido com sucesso.")
        return user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from implantdetect_shared.entities.user import User
from implantdetect_shared.models.dtos.user_dto import (
    UserUpdateRequest,
    UserRegisterRequest,
)


class UserDao:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_users(self) -> list[User]:
        result = await self.db.execute(select(User))
        return list(result.scalars().all())

    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()

    async def add_user(self, user: UserRegisterRequest, hashed_password: str) -> User:
        user_data = user.model_dump()
        user_data.pop("password")
        user_data["hashed_password"] = hashed_password
        user_entity = User(**user_data)
        self.db.add(user_entity)
        await self.db.commit()
        await self.db.refresh(user_entity)
        return user_entity

    async def update_user(
        self, updated_user_data: UserUpdateRequest, hash_password_fn
    ) -> User | None:
        user = await self.get_user_by_id(updated_user_data.user_id)
        if not user:
            return None
        if updated_user_data.username is not None:
            user.username = updated_user_data.username
        if updated_user_data.email is not None:
            user.email = updated_user_data.email
        if updated_user_data.password is not None:
            user.hashed_password = hash_password_fn(updated_user_data.password)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_by_username_or_email(self, identifier: str) -> User | None:
        result = await self.db.execute(
            select(User).filter(
                or_(User.username == identifier, User.email == identifier)
            )
        )
        return result.scalars().first()

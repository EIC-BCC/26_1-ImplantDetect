from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from models.entities.user import User
from core.security import hash_password
from enums.general_status import GeneralStatus
from models.dtos.user_dto import UserUpdateRequest, UserRegisterRequest

class UserDao:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()

    async def add_user(self, user: UserRegisterRequest) -> User:
        user_data = user.model_dump()
        password = user_data.pop('password')
        user_data['hashed_password'] = hash_password(password)
        user_entity = User(**user_data)
        self.db.add(user_entity)
        await self.db.commit()
        await self.db.refresh(user_entity)
        return user_entity

    # async def remove_user(self, user_id: int) -> User | None:
    #     user = await self.get_user_by_id(user_id)
    #     if user:
    #         setattr(user, 'active', GeneralStatus.INACTIVE)
    #         self.db.add(user)
    #         await self.db.commit()
    #         return user
    #     return None

    async def update_user(self, updated_user_data: UserUpdateRequest) -> User | None:
        user = await self.get_user_by_id(updated_user_data.user_id)
        if user:
            for key, value in updated_user_data.model_dump().items():
                setattr(user, key, value)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        return None

    async def get_all_active_users(self) -> list[User]:
        result = await self.db.execute(
            select(User).filter(User.active == GeneralStatus.ACTIVE)
        )
        return list(result.scalars().all())

    async def get_user_by_username_or_email(self, identifier: str) -> User | None:
        result = await self.db.execute(
            select(User).filter(
                or_(User.username == identifier, User.email == identifier)
            )
        )
        return result.scalars().first()
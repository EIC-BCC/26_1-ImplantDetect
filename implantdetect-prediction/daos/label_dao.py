from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.entities.label import Label


class LabelDao:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_label_by_name(self, name: str) -> Label | None:
        result = await self.db.execute(select(Label).filter(Label.name == name))
        return result.scalars().first()

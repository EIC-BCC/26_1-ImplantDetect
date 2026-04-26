from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.entities.process import Process
from models.entities.process_results import ProcessResults


class ProcessDao:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_process_by_id(self, process_id: int) -> Process | None:
        result = await self.db.execute(select(Process).filter(Process.id == process_id))
        return result.scalars().first()

    async def update_process_status(self, process_id: int, status: int) -> Process | None:
        process = await self.get_process_by_id(process_id)
        if process:
            setattr(process, 'status', status)
            self.db.add(process)
            await self.db.commit()
            await self.db.refresh(process)
            return process
        return None

    async def add_process_result(self, process_result: ProcessResults) -> ProcessResults:
        self.db.add(process_result)
        await self.db.commit()
        await self.db.refresh(process_result)
        return process_result

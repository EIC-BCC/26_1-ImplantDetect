from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.entities.process import Process
from models.entities.process_results import ProcessResults
from enums.process_status import ProcessStatus

class ProcessDao:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_process_by_id(self, process_id: int) -> Process | None:
        result = await self.db.execute(select(Process).filter(Process.id == process_id))
        return result.scalars().first()

    async def add_process(self, process: Process) -> Process:
        self.db.add(process)
        await self.db.commit()
        await self.db.refresh(process)
        return process

    async def update_process_status(self, process_id: int, status: int) -> Process | None:
        process = await self.get_process_by_id(process_id)
        if process:
            setattr(process, 'status', status)
            self.db.add(process)
            await self.db.commit()
            await self.db.refresh(process)
            return process
        return None

    async def get_all_processes_by_user(self, user_id: int) -> list[Process]:
        result = await self.db.execute(
            select(Process).filter(Process.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_processes_by_status(self, status: int) -> list[Process]:
        result = await self.db.execute(
            select(Process).filter(Process.status == status)
        )
        return list(result.scalars().all())

    async def add_process_result(self, process_result: ProcessResults) -> ProcessResults:
        self.db.add(process_result)
        await self.db.commit()
        await self.db.refresh(process_result)
        return process_result

    async def get_results_by_process_id(self, process_id: int) -> list[ProcessResults]:
        result = await self.db.execute(
            select(ProcessResults).filter(ProcessResults.process_id == process_id)
        )
        return list(result.scalars().all())

    async def cancel_process(self, process_id: int) -> Process | None:
        process = await self.get_process_by_id(process_id)
        if process and process.status in [ProcessStatus.PENDING, ProcessStatus.RUNNING]:
            setattr(process, 'status', ProcessStatus.CANCELED)
            self.db.add(process)
            await self.db.commit()
            await self.db.refresh(process)
            return process
        return None
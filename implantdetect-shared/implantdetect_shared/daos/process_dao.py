from sqlalchemy import update
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from implantdetect_shared.entities.process import Process
from implantdetect_shared.entities.process_results import ProcessResults


class ProcessDao:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_process_by_id(self, process_id: int) -> Process | None:
        result = await self.db.execute(select(Process).filter(Process.id == process_id))
        return result.scalars().first()

    async def add_process(self, process: Process) -> Process:
        self.db.add(process)
        await self.db.flush()
        await self.db.refresh(process)
        return process

    async def update_process_status(
        self, process_id: int, status: int
    ) -> Process | None:
        process = await self.get_process_by_id(process_id)
        if process:
            setattr(process, "status", status)
            self.db.add(process)
            await self.db.flush()
            await self.db.refresh(process)
            return process
        return None

    async def get_all_processes(
        self, limit: int = 50, offset: int = 0
    ) -> list[Process]:
        result = await self.db.execute(
            select(Process).order_by(Process.id).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def get_all_processes_by_user(
        self, user_id: int, limit: int = 50, offset: int = 0
    ) -> list[Process]:
        result = await self.db.execute(
            select(Process)
            .filter(Process.user_id == user_id)
            .order_by(Process.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_results_by_process_id(self, process_id: int) -> list[ProcessResults]:
        result = await self.db.execute(
            select(ProcessResults).filter(ProcessResults.process_id == process_id)
        )
        return list(result.scalars().all())

    async def add_process_result(
        self, process_result: ProcessResults
    ) -> ProcessResults:
        self.db.add(process_result)
        await self.db.flush()
        await self.db.refresh(process_result)
        return process_result

    async def fail_stale_processes(
        self, failed_status: int, stale_statuses: list[int]
    ) -> int:
        cursor: CursorResult = await self.db.execute(  # type: ignore[assignment]
            update(Process)
            .where(Process.status.in_(stale_statuses))
            .values(status=failed_status)
        )
        return cursor.rowcount

from typing import NoReturn
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import get_logger
from core.configuration import settings
from implantdetect_shared.daos.label_dao import LabelDao
from implantdetect_shared.daos.process_dao import ProcessDao
from implantdetect_shared.daos.image_dao import ImageDAO
from implantdetect_shared.entities.process import Process
from implantdetect_shared.entities.image import Image
from implantdetect_shared.models.dtos.process_dto import (
    ProcessResultsResponse,
    ProcessResponse,
)
from implantdetect_shared.enums.process_status import ProcessStatus
from services.queue_service import queue_service

logger = get_logger(__name__)


class ProcessService:
    def __init__(self, db: AsyncSession):
        self.process_dao = ProcessDao(db)
        self.label_dao = LabelDao(db)
        self.image_dao = ImageDAO(db, settings.IMAGE_REPOSITORY)

    async def add_process(self, image: Image):
        if not image:
            logger.error("Imagem não fornecida para o processo.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Imagem não fornecida para o processo.",
            )

        if image.file_extension is None:
            logger.error(f"Imagem {image.file_hash} sem extensão de arquivo.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Imagem sem extensão de arquivo.",
            )

        process = Process(
            user_id=image.user_id, image_id=image.id, status=ProcessStatus.PENDING
        )
        new_process = await self.process_dao.add_process(process)
        logger.info(
            f"Processo {new_process.id} criado da imagem {image.file_hash} para o usuário {image.user_id}."
        )

        try:
            await queue_service.publish_prediction_request(
                new_process.id, image.file_hash, image.file_extension
            )
        except Exception as e:
            logger.error(f"Erro ao enfileirar processo {new_process.id}: {e}")
            await self.process_dao.update_process_status(
                new_process.id, ProcessStatus.FAILED
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao enfileirar predição",
            )

        return new_process.id

    async def _handle_process_not_found(self) -> NoReturn:
        logger.error("Processo não encontrado.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Processo não encontrado."
        )

    async def get_process(self, process_id: int) -> ProcessResponse:
        process = await self.process_dao.get_process_by_id(process_id)
        if not process:
            await self._handle_process_not_found()
        logger.info(f"Processo {process.id} recuperado com sucesso.")

        image = await self.image_dao.get_image_by_id(process.image_id)
        status_value = getattr(process, "status", 0)
        status_name = self._get_status_name(status_value)
        return ProcessResponse.from_orm(process, status_name, image)

    async def get_all_processes_by_user(
        self, user_id: int, limit: int = 50, offset: int = 0
    ) -> list[ProcessResponse]:
        processes = await self.process_dao.get_all_processes_by_user(
            user_id, limit=limit, offset=offset
        )
        logger.info(
            f"{len(processes)} processos recuperados para usuário ID={user_id}."
        )

        return [
            ProcessResponse.from_orm(
                process, self._get_status_name(getattr(process, "status", 0))
            )
            for process in processes
        ]

    async def get_results_by_process_id(
        self, process_id: int
    ) -> list[ProcessResultsResponse]:
        process = await self.process_dao.get_process_by_id(process_id)
        if not process:
            await self._handle_process_not_found()

        results = await self.process_dao.get_results_by_process_id(process_id)
        logger.info(
            f"{len(results)} resultados recuperados para o processo {process_id}."
        )
        image = await self.image_dao.get_image_by_id(process.image_id)

        # Bulk fetch de labels — uma única query para todos os class_ids
        class_ids = {
            r.class_id for r in results if getattr(r, "class_id", None) is not None
        }
        labels = await self.label_dao.get_labels_by_ids(class_ids)
        label_map = {label.id: str(label.name) for label in labels}

        return [
            ProcessResultsResponse.from_orm(
                result,
                label_map.get(result.class_id, f"Classe {result.class_id}"),
                image,
            )
            for result in results
        ]

    def _get_status_name(self, status_id: int) -> str:
        try:
            return ProcessStatus(status_id).label
        except ValueError:
            return f"Status {status_id}"

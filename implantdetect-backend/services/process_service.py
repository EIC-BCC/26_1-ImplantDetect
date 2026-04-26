from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import get_logger
from daos.label_dao import LabelDao
from daos.process_dao import ProcessDao
from models.entities.process import Process
from models.entities.image import Image
from daos.image_dao import ImageDAO
from models.dtos.process_dto import ProcessResultsResponse, ProcessResponse
from enums.process_status import ProcessStatus
from services.queue_service import queue_service

logger = get_logger(__name__)


class ProcessService:
    def __init__(self, db: AsyncSession):
        self.process_dao = ProcessDao(db)
        self.label_dao = LabelDao(db)
        self.image_dao = ImageDAO(db)

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

    async def _handle_process_not_found(self):
        logger.error("Processo não encontrado.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Processo não encontrado."
        )

    async def get_process(self, process_id: int) -> ProcessResponse:
        process = await self.process_dao.get_process_by_id(process_id)
        if not process:
            await self._handle_process_not_found()
        logger.info(f"Processo {process.id} recuperado com sucesso.")

        status_value = getattr(process, "status", 0)
        status_name = self._get_status_name(status_value)
        return ProcessResponse.from_orm(process, status_name)

    async def get_all_processes_by_user(self, user_id: int) -> list[ProcessResponse]:
        processes = await self.process_dao.get_all_processes_by_user(user_id)
        logger.info(f"{len(processes)} processos recuperados para o usuário {user_id}.")

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

        response = []
        for result in results:
            class_id_value = getattr(result, "class_id", 0)
            class_name = await self._get_label_name(class_id_value)
            response.append(ProcessResultsResponse.from_orm(result, class_name, image))
        return response

    async def _get_label_name(self, class_id: int) -> str:
        label = await self.label_dao.get_label_by_id(class_id)
        if not label:
            logger.warning(f"Classe {class_id} não encontrada.")
            return f"Classe {class_id}"
        return str(label.name)

    def _get_status_name(self, status_id: int) -> str:
        status_mapping = {
            ProcessStatus.PENDING: "Pendente",
            ProcessStatus.RUNNING: "Executando",
            ProcessStatus.COMPLETED: "Concluído",
            ProcessStatus.FAILED: "Falhou",
            ProcessStatus.CANCELED: "Cancelado",
        }
        return status_mapping.get(status_id, f"Status {status_id}")

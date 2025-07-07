from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import get_logger
from daos.label_dao import LabelDao
from daos.process_dao import ProcessDao
from models.entities.process import Process
from models.entities.image import Image
from models.entities.process_results import ProcessResults
from models.dtos.process_dto import ProcessResultsResponse, ProcessResponse
from enums.process_status import ProcessStatus
from wrapper.yolo_wrapper import YoloWrapper

logger = get_logger(__name__)

class ProcessService:
    def __init__(self, db: AsyncSession):
        self.process_dao = ProcessDao(db)
        self.label_dao = LabelDao(db)
        self.model = YoloWrapper()

    async def _handle_process_not_found(self):
        logger.error("Processo não encontrado.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Process not found"
        )

    async def add_process(self, image: Image):
        """
        Adiciona um novo processo ao sistema.
        """
        if not image:
            logger.error("Imagem não fornecida para o processo.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image not provided for the process"
            )

        process = Process(
            user_id=image.user_id,
            image_id=image.id,
            status=ProcessStatus.PENDING
        )

        new_process = await self.process_dao.add_process(process)
        logger.info(f"Processo {new_process.id} criado da imagem {image.file_hash} para o usuário {image.user_id}.")

        try:
            if image.file_extension is None:
                logger.error(f"Image {image.file_hash} has no file extension.")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Image has no file extension"
                )
            
            predictions = await self.model.predict(image.file_hash, image.file_extension)
            await self._handle_predictions(new_process, predictions, image.file_hash)
            return new_process
        except Exception as e:
            await self._handle_processing_error(new_process, image.file_hash, e)

    async def _handle_predictions(self, process: Process, predictions: list, file_hash: str):
        if not predictions:
            logger.warning(f"Nenhuma previsão feita para a imagem {file_hash}.")
            await self.process_dao.update_process_status(process.id, ProcessStatus.COMPLETED)
        else:
            await self.process_dao.update_process_status(process.id, ProcessStatus.COMPLETED)
            for prediction in predictions:
                result = ProcessResults(
                    process_id=process.id,
                    class_id=prediction.class_id,
                    confidence=prediction.confidence,
                    bounding_box=prediction.bounding_box
                )
                await self.process_dao.add_process_result(result)

    async def _handle_processing_error(self, process: Process, file_hash: str, error: Exception):
        logger.error(f"Erro ao processar a imagem {file_hash}: {str(error)}")
        await self.process_dao.update_process_status(process.id, ProcessStatus.FAILED)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(error)}"
        )

    async def get_process(self, process_id: int) -> ProcessResponse:
        process = await self.process_dao.get_process_by_id(process_id)
        if not process:
            await self._handle_process_not_found()
        logger.info(f"Processo {process.id} recuperado com sucesso.")
        
        status_value = getattr(process, 'status', 0)
        status_name = self._get_status_name(status_value)
        return ProcessResponse.from_orm(process, status_name)

    async def update_process_status(self, process_id: int, status: int):
        process = await self.process_dao.update_process_status(process_id, status)
        if not process:
            await self._handle_process_not_found()
        logger.info(f"Status do processo {process.id} atualizado para {status}.")
        return process

    async def get_all_processes_by_user(self, user_id: int) -> list[ProcessResponse]:
        processes = await self.process_dao.get_all_processes_by_user(user_id)
        logger.info(f"{len(processes)} processos recuperados para o usuário {user_id}.")
        
        return [
            ProcessResponse.from_orm(process, self._get_status_name(getattr(process, 'status', 0)))
            for process in processes
        ]

    # async def get_processes_by_status(self, status: int):
    #     processes = await self.process_dao.get_processes_by_status(status)
    #     logger.info(f"{len(processes)} processos com status {status} recuperados.")
    #     return processes

    async def add_process_result(self, process_result: ProcessResults):
        result = await self.process_dao.add_process_result(process_result)
        logger.info(f"Resultado do processo {result.process_id} adicionado com sucesso.")
        return result

    async def get_results_by_process_id(self, process_id: int) -> list[ProcessResultsResponse]:
        results = await self.process_dao.get_results_by_process_id(process_id)
        logger.info(f"{len(results)} resultados recuperados para o processo {process_id}.")
        
        response = []
        for result in results:
            class_id_value = getattr(result, 'class_id', 0)
            class_name = await self._get_label_name(class_id_value)
            response.append(ProcessResultsResponse.from_orm(result, class_name))
        return response
    
    async def _get_label_name(self, class_id: int) -> str:
        """
        Mapeia o class_id para o nome da classe.
        Adapte conforme suas classes de detecção.
        """
        
        label = await self.label_dao.get_label_by_id(class_id)
        if not label:
            logger.warning(f"Classe {class_id} não encontrada.")
            return f"Classe {class_id}"
        return str(label.name)
    
    def _get_status_name(self, status_id: int) -> str:
        """
        Mapeia o status_id para o nome do status.
        """
        status_mapping = {
            ProcessStatus.PENDING: "Pendente",
            ProcessStatus.RUNNING: "Executando",
            ProcessStatus.COMPLETED: "Concluído",
            ProcessStatus.FAILED: "Falhou",
            ProcessStatus.CANCELED: "Cancelado"
        }
        return status_mapping.get(status_id, f"Status {status_id}")
    
    # async def cancel_process(self, process_id: int):
    #     process = await self.dao.cancel_process(process_id)
    #     if not process:
    #         await self._handle_process_not_found()
    #     logger.info(f"Processo {process.id} cancelado com sucesso.")
    #     return process
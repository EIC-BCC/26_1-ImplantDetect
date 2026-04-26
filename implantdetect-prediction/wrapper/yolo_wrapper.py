import json
from ultralytics import YOLO

from core.logging import get_logger
from core.configuration import settings
from models.dtos.process_dto import ProcessPredictionResponse

logger = get_logger(__name__)


class YoloWrapper:
    def __init__(self):
        self.model = YOLO(settings.YOLO_MODEL_PATH)

    async def _generate_file_location(self, file_hash: str, file_extension: str) -> str:
        return f"{settings.UPLOAD_FILE_PATH}/{file_hash}{file_extension}"

    async def predict(self, file_hash: str, file_extension: str) -> list[ProcessPredictionResponse]:
        logger.info(f"Executando YOLO no modelo: {settings.YOLO_MODEL_PATH}")
        file_location = await self._generate_file_location(file_hash, file_extension)
        results = self.model.predict(
            source=file_location,
            conf=0.1
        )

        if not results:
            logger.error(f"Nenhuma predição encontrada para {file_hash}.")
            return []

        predictions = []
        for result in results:
            r = json.loads(result.to_json())
            for pred in r:
                predictions.append(ProcessPredictionResponse.from_dict(pred))

        if not predictions:
            logger.warning(f"Nenhuma predição feita para {file_hash}.")
        else:
            logger.info(f"Predições para {file_hash}: {len(predictions)} caixas detectadas.")

        return predictions

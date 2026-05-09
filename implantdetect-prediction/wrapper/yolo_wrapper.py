import json
import asyncio
from functools import partial
from ultralytics import YOLO

from core.logging import get_logger
from core.configuration import settings
from implantdetect_shared.models.dtos.process_dto import ProcessPredictionResponse

logger = get_logger(__name__)


class YoloWrapper:
    def __init__(self):
        self.model = YOLO(settings.YOLO_MODEL_PATH)

    def _generate_file_location(self, file_hash: str, file_extension: str) -> str:
        return f"{settings.UPLOAD_FILE_PATH}/{file_hash}{file_extension}"

    def _run_inference(self, file_location: str) -> list[ProcessPredictionResponse]:
        """Executa a inferência YOLO de forma síncrona (chamada via thread pool)."""
        results = self.model.predict(source=file_location, conf=0.1)

        if not results:
            logger.error(f"Nenhuma predição encontrada para {file_location}.")
            return []

        predictions = []
        for result in results:
            r = json.loads(result.to_json())
            for pred in r:
                predictions.append(ProcessPredictionResponse.from_dict(pred))

        return predictions

    async def predict(
        self, file_hash: str, file_extension: str
    ) -> list[ProcessPredictionResponse]:
        logger.info(f"Executando YOLO no modelo: {settings.YOLO_MODEL_PATH}")
        file_location = self._generate_file_location(file_hash, file_extension)

        # Inferência YOLO é CPU/GPU-bound — executar em thread pool para não bloquear event loop
        loop = asyncio.get_running_loop()
        predictions = await loop.run_in_executor(
            None, partial(self._run_inference, file_location)
        )

        if not predictions:
            logger.warning(f"Nenhuma predição feita para {file_hash}.")
        else:
            logger.info(
                f"Predições para {file_hash}: {len(predictions)} caixas detectadas."
            )

        return predictions

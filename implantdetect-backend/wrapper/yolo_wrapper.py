from ultralytics import YOLO
from core.logging import get_logger
from core.configuration import settings
from models.dtos.process_dto import ProcessPredictionResponse
import json

logger = get_logger(__name__)

class YoloWrapper:
    def __init__(self):
        self.model = YOLO(settings.YOLO_MODEL_PATH)
        
    async def _generate_file_location(self, file_hash: str, file_extension: str) -> str:
        return f"{settings.UPLOAD_FILE_PATH}/{file_hash}{file_extension}"

    async def predict(self, file_hash: str, file_extension: str) -> list[ProcessPredictionResponse]:
        print("Running yolo on model: " + settings.YOLO_MODEL_PATH)
        file_location = await self._generate_file_location(file_hash, file_extension)
        results = self.model.predict(
            source=file_location,
            conf=0.1
        )

        print(f"Results: {results}")

        if not results:
            logger.error(f"No predictions found for {file_hash}.")
            return []

        predictions = []
        for result in results:
            r = json.loads(result.to_json())
            for pred in r:
                print(pred)
                predictions.append(ProcessPredictionResponse.from_dict(pred))

        if not predictions:
            logger.warning(f"No predictions made for {file_hash}.")
        else:
            logger.info(f"Predictions made for {file_hash}: {len(predictions)} boxes detected.")

        return predictions
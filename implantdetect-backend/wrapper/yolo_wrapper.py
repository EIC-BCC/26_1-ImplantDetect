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
            boxes = getattr(result, 'boxes', None)
            if boxes and hasattr(boxes, '__iter__'):
                for box in boxes:
                    predictions.append(
                        ProcessPredictionResponse(
                            class_id=int(getattr(box, 'cls', -1)),
                            confidence=float(getattr(box, 'conf', 0.0)),
                            bounding_box=getattr(box, 'xyxy', [])
                        )
                    )
            else:
                logger.warning(f"No valid bounding boxes found in the result for {file_hash}.")

        if not predictions:
            logger.warning(f"No predictions made for {file_hash}.")
        else:
            logger.info(f"Predictions made for {file_hash}: {len(predictions)} boxes detected.")

        return predictions
from ultralytics import YOLO
from core.logging import get_logger
from core.configuration import settings
from models.dtos.process_dto import ProcessPredictionResponse

logger = get_logger(__name__)

class YoloWrapper:
    def __init__(self):
        self.model = YOLO('yolo11m-obb.pt')
        
    async def _generate_file_location(self, filename: str) -> str:
        return f"{settings.UPLOAD_FILE_PATH}/{filename}"
        
    async def predict(self, filename: str) -> list[ProcessPredictionResponse]:
        file_location = await self._generate_file_location(filename)
        results = self.model.predict(file_location)

        if not results:
            logger.error(f"No predictions found for {filename}.")
            return []

        predictions = []
        for result in results:
            boxes = getattr(result, 'boxes', None)
            if boxes:
                for box in boxes:
                    predictions.append(
                        ProcessPredictionResponse(
                            class_id=int(getattr(box, 'cls', -1)),
                            confidence=float(getattr(box, 'conf', 0.0)),
                            bounding_box=getattr(box, 'xyxy', [])
                        )
                    )
            else:
                logger.warning(f"No bounding boxes found in the result for {filename}.")

        if not predictions:
            logger.warning(f"No predictions made for {filename}.")
        else:
            logger.info(f"Predictions made for {filename}: {len(predictions)} boxes detected.")

        return predictions
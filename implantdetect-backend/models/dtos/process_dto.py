from pydantic import BaseModel
from datetime import datetime

class ProcessPredictionResponse(BaseModel):
    class_id: int
    confidence: float
    bounding_box: list[float]
    
class ProcessResultsResponse(BaseModel):
    process_id: int
    class_id: int
    class_name: str
    confidence: float
    bounding_box: str
    probability: float
    message: str | None

    @classmethod
    def from_orm(cls, result, class_name: str = "Unknown"):
        return cls(
            process_id=result.process_id,
            class_id=result.class_id,
            class_name=class_name,
            confidence=result.confidence,
            bounding_box=result.bounding_box,
            probability=result.probability,
            message=result.message
        )

class ProcessResponse(BaseModel):
    process_id: int
    user_id: int
    image_id: int
    status: int
    status_name: str
    created_at: str
    updated_at: str

    @classmethod
    def from_orm(cls, process, status_name: str = "Unknown"):
        return cls(
            process_id=process.id,
            user_id=process.user_id,
            image_id=process.image_id,
            status=process.status,
            status_name=status_name,
            created_at=str(process.created_at),
            updated_at=str(process.updated_at)
        )
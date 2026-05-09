from typing import Optional
from pydantic import BaseModel
from typing_extensions import TypedDict

from implantdetect_shared.entities.image import Image


class ProcessResultsResponse(BaseModel):
    process_id: int
    class_name: str
    confidence: float | None
    bb_x1_center: float | None
    bb_y1_center: float | None
    bb_x2_center: float | None
    bb_y2_center: float | None
    bb_x3_center: float | None
    bb_y3_center: float | None
    bb_x4_center: float | None
    bb_y4_center: float | None
    message: str | None
    image_url: str | None = None

    @classmethod
    def from_orm(
        cls, result, class_name: str = "Unknown", image: Optional[Image] = None
    ):
        return cls(
            process_id=result.process_id,
            class_name=class_name,
            confidence=result.confidence,
            bb_x1_center=result.bb_x1_center,
            bb_y1_center=result.bb_y1_center,
            bb_x2_center=result.bb_x2_center,
            bb_y2_center=result.bb_y2_center,
            bb_x3_center=result.bb_x3_center,
            bb_y3_center=result.bb_y3_center,
            bb_x4_center=result.bb_x4_center,
            bb_y4_center=result.bb_y4_center,
            message=result.message,
            image_url=image.file_hash + image.file_extension if image else None,
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
            updated_at=str(process.updated_at),
        )


class OBBCorners(TypedDict):
    x1: float
    y1: float
    x2: float
    y2: float
    x3: float
    y3: float
    x4: float
    y4: float


class ProcessPredictionResponse(BaseModel):
    class_name: str
    confidence: float
    bounding_box: OBBCorners

    @staticmethod
    def from_dict(data: dict) -> "ProcessPredictionResponse":
        return ProcessPredictionResponse(
            class_name=data.get("name", ""),
            confidence=data.get("confidence", 0.0),
            bounding_box=data.get("box", {}),
        )

from pydantic import BaseModel
from typing_extensions import TypedDict


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
    def from_dict(data: dict) -> 'ProcessPredictionResponse':
        return ProcessPredictionResponse(
            class_name=data.get('name', ''),
            confidence=data.get('confidence', 0.0),
            bounding_box=data.get('box', {}),
        )

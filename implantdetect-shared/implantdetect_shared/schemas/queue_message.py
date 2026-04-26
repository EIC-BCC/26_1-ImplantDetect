from pydantic import BaseModel


class PredictionRequest(BaseModel):
    process_id: int
    file_hash: str
    file_extension: str

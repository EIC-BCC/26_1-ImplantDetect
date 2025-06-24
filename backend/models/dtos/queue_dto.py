from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class QueueRequest(BaseModel):
    image_id: int
    user_id: int
    
class QueueResponse(BaseModel):
    id: int
    image_id: int
    user_id: int
    id_status: int
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    @classmethod
    def from_orm(cls, queue):
        return cls(
            id=queue.id,
            image_id=queue.image_id,
            user_id=queue.user_id,
            id_status=queue.id_status,
            created_at=queue.created_at,
            started_at=queue.started_at,
            finished_at=queue.finished_at,
            error_message=queue.error_message
        )
    
class QueueListResponse(BaseModel):
    queues: List[QueueResponse]
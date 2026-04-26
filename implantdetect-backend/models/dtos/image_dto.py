from pydantic import BaseModel

class ImageResponse(BaseModel):
    image_id: int
    user_id: int
    filename: str
    submitted_at: str | None = None
    active: bool | None = None

    @classmethod
    def from_orm(cls, image):
        return cls(
            image_id=image.id,
            user_id=image.user_id,
            filename=image.file_hash + image.file_extension,
            submitted_at=str(image.submitted_at) if hasattr(image, 'submitted_at') else None,
            active=bool(image.active) if hasattr(image, 'active') else None
        )
        
class ImageUploadResponse(BaseModel):
    image_id: int
    process_id: int
    
    @classmethod
    def from_orm(cls, image_id, process_id):
        return cls(
            image_id=image_id,
            process_id=process_id
        )
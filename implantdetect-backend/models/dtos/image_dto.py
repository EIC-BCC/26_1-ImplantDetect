from pydantic import BaseModel

class ImageUploadRequest(BaseModel):
    image: bytes
    user_id: int
    
class ImageResponse(BaseModel):
    image_id: int
    user_id: int
    image_path: str
    submitted_at: str | None = None
    active: bool | None = None

    @classmethod
    def from_orm(cls, image):
        return cls(
            image_id=image.id,
            user_id=image.user_id,
            image_path=image.path.replace('\\uploads\\', ''),
            submitted_at=str(image.submitted_at) if hasattr(image, 'submitted_at') else None,
            active=bool(image.active) if hasattr(image, 'active') else None
        )
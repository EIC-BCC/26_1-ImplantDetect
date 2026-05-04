from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from core.security import get_current_user, JWTPayload
from implantdetect_shared.models.dtos.result_dto import Result
from implantdetect_shared.models.dtos.image_dto import (
    ImageResponse,
    ImageUploadResponse,
)
from services.image_service import ImageService

router = APIRouter()


@router.post("/submit", response_model=Result)
async def submit_image(
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db),
    user: JWTPayload = Depends(get_current_user),
):
    user_id = int(user["sub"])
    image_service = ImageService(db)
    image_id, process_id = await image_service.handle_image_upload(image, user_id)
    return Result.ok(
        data=ImageUploadResponse.from_orm(image_id, process_id).model_dump()
    )


@router.get("/user", response_model=Result)
async def get_user_images(
    db: AsyncSession = Depends(get_async_db),
    user: JWTPayload = Depends(get_current_user),
):
    user_id = int(user["sub"])
    image_service = ImageService(db)
    images = await image_service.get_all_images_from_user(user_id)
    return Result.ok(data={"images": [img.model_dump() for img in images]})


@router.get("/{image_id}", response_model=Result)
async def get_image(
    image_id: int,
    db: AsyncSession = Depends(get_async_db),
    user: JWTPayload = Depends(get_current_user),
):
    image_service = ImageService(db)
    image = await image_service.get_image_by_id(image_id)
    return Result.ok(data=ImageResponse.from_orm(image).model_dump())

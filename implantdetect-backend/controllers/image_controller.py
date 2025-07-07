from fastapi import APIRouter, Depends, UploadFile

from core.database import get_async_db
from models.dtos.result_dto import Result
from core.security import get_current_user
from models.dtos.image_dto import ImageResponse
from services.image_service import ImageService

router = APIRouter()

@router.post("/submit", response_model=Result)
async def submit_image(image: UploadFile, db=Depends(get_async_db), user=Depends(get_current_user)):
    user_id = int(user["sub"])
    image_service = ImageService(db)
    image_id = await image_service.handle_image_upload(image, user_id)
    return Result.ok(message="Imagem salva com sucesso.", data={"image_id": image_id})

@router.get("/user", response_model=Result)
async def get_user_images(db=Depends(get_async_db), user=Depends(get_current_user)):
    user_id = int(user["sub"])
    image_service = ImageService(db)
    images = await image_service.get_all_images_from_user(user_id)
    return Result.ok(data={"images": [img.model_dump() for img in images]})

@router.get("/{image_id}", response_model=Result)
async def get_image(image_id: int, db=Depends(get_async_db), user=Depends(get_current_user)):
    image_service = ImageService(db)
    image = await image_service.get_image_by_id(image_id)
    return Result.ok(data=ImageResponse.from_orm(image).model_dump())

# @router.post("/update/{image_id}", response_model=Result)
# async def update_image(image_id: int, updated_data: dict, db=Depends(get_async_db), user=Depends(get_current_user)):
#     image_service = ImageService(db)
#     await image_service.update_image(image_id, updated_data)
#     return Result.ok(message="Imagem atualizada com sucesso.")

# @router.delete("/delete/{image_id}", response_model=Result)
# async def delete_image(image_id: int, db=Depends(get_async_db), user=Depends(get_current_user)):
#     image_service = ImageService(db)
#     await image_service.remove_image(image_id)
#     return Result.ok(message="Imagem removida com sucesso.")
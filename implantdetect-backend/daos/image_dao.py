import os
import uuid
from pathlib import Path
from datetime import datetime
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import get_logger
from core.configuration import settings
from models.entities.image import Image
from enums.general_status import GeneralStatus

logger = get_logger(__name__)

class ImageDAO:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.image_repository = settings.IMAGE_REPOSITORY

    async def get_image_by_id(self, image_id: int) -> Image | None:
        result = await self.db.execute(select(Image).filter(Image.id == image_id))
        return result.scalars().first()

    async def save_image(self, image: UploadFile) -> str:
        try:
            assert image.filename is not None, "O nome do arquivo não pode ser nulo."
            
            file_extension = Path(image.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            image_path = os.path.join(self.image_repository, unique_filename)
            
            contents = await image.read()
            
            with open(image_path, "wb") as f:
                f.write(contents)
                
            return unique_filename
        
        except Exception as e:
            logger.error(f"Erro ao salvar a imagem: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao salvar a imagem: {str(e)}"
            )

    async def add_image(self, image: Image) -> Image:
        try:
            self.db.add(image)
            await self.db.flush()
            await self.db.refresh(image)
            return image
        
        except Exception as e:
            logger.error(f"Erro ao adicionar imagem ao banco de dados: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao adicionar imagem ao banco de dados: {str(e)}"
            )

    async def remove_image(self, image_id: int) -> Image | None:
        image = await self.get_image_by_id(image_id)
        
        if image:
            setattr(image, 'active', GeneralStatus.INACTIVE)
            self.db.add(image)
            await self.db.commit()
            return image
        
        return None

    async def update_image(self, image_id: int, updated_data: dict) -> Image | None:
        image = await self.get_image_by_id(image_id)
        
        if image:
            for key, value in updated_data.items():
                setattr(image, key, value)
            self.db.add(image)
            await self.db.commit()
            await self.db.refresh(image)
            return image
        
        return None

    async def get_all_images_from_user(self, user_id: int):
        result = await self.db.execute(
            select(Image).filter(Image.user_id == user_id)
        )
        return list(result.scalars().all())

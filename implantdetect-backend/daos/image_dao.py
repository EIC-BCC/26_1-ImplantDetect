import hashlib
from pathlib import Path
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

    def _get_image_hash(self, image: UploadFile) -> str:
        hasher = hashlib.sha256()
        image.file.seek(0)
        while chunk := image.file.read(4096):
            hasher.update(chunk)
        image.file.seek(0)
        return hasher.hexdigest()

    async def save_image(self, image: UploadFile) -> tuple[str, str]:
        try:
            assert image.filename is not None, "O nome do arquivo não pode ser nulo."

            file_extension = Path(image.filename).suffix
            file_hash = self._get_image_hash(image)

            existing_image = await self.get_image_by_hash(file_hash, file_extension)
            if existing_image:
                logger.info("Imagem já existe no banco de dados.")
                return str(existing_image.file_hash), str(existing_image.file_extension)

            folder = Path(self.image_repository)
            image_path = f"{folder}/{file_hash}{file_extension}"
            contents = await image.read()
            with open(image_path, "wb") as f:
                f.write(contents)

            logger.info(f"Imagem salva como: {str(image_path)}")
            return file_hash, file_extension

        except Exception as e:
            logger.error(f"Erro ao salvar a imagem: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao salvar a imagem: {str(e)}",
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
                detail=f"Erro ao adicionar imagem ao banco de dados: {str(e)}",
            )

    async def get_all_images_from_user(self, user_id: int):
        result = await self.db.execute(
            select(Image).filter(
                Image.user_id == user_id, Image.active == GeneralStatus.ACTIVE
            )
        )
        return list(result.scalars().all())

    async def get_image_by_id(self, image_id: int) -> Image | None:
        result = await self.db.execute(select(Image).filter(Image.id == image_id))
        return result.scalars().first()

    async def get_image_by_hash(
        self, file_hash: str, file_extension: str
    ) -> Image | None:
        result = await self.db.execute(
            select(Image).filter(
                Image.file_hash == file_hash, Image.file_extension == file_extension
            )
        )
        return result.scalars().first()

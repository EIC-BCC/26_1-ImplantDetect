import io
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException, status
from PIL import Image as PILImage, UnidentifiedImageError

from core.logging import get_logger
from core.configuration import settings
from implantdetect_shared.daos.image_dao import ImageDAO
from implantdetect_shared.entities.image import Image
from implantdetect_shared.models.dtos.image_dto import ImageResponse
from services.process_service import ProcessService

logger = get_logger(__name__)


class ImageService:
    def __init__(self, db: AsyncSession):
        self._init_configurations()
        self.image_dao = ImageDAO(db, settings.IMAGE_REPOSITORY)
        self.process_service = ProcessService(db)

    def _handle_image_not_found(self):
        logger.error("Imagem não encontrada.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Imagem não encontrada."
        )

    def _init_configurations(self) -> None:
        self.image_maximum_size = settings.IMAGE_MAXIMUM_SIZE
        self.image_supported_formats = [
            f.lower() for f in settings.IMAGE_SUPPORTED_FORMATS
        ]

    def _check_size(self, size: int) -> None:
        if size > self.image_maximum_size:
            size_mb = size / (1024 * 1024)
            max_size_mb = self.image_maximum_size / (1024 * 1024)
            logger.warning(f"Imagem muito grande: {size_mb:.2f} MB.")
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Imagem muito grande: {size_mb:.2f} MB. Máximo: {max_size_mb:.2f} MB.",
            )

    def _check_format(self, fmt: str) -> None:
        if fmt.lower() not in self.image_supported_formats:
            logger.warning(f"Formato de imagem não suportado: {fmt}")
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Formato não suportado: {fmt}. Suportados: {', '.join(self.image_supported_formats)}.",
            )

    async def _validate_image(self, image: UploadFile) -> None:
        try:
            await image.seek(0)
            data = await image.read()
            self._check_size(len(data))

            try:
                fmt = PILImage.open(io.BytesIO(data)).format
            except UnidentifiedImageError:
                fmt = None

            if not fmt:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Arquivo enviado não é uma imagem válida.",
                )

            self._check_format(fmt)
            await image.seek(0)

            logger.info(f"Imagem validada: formato {fmt}, tamanho {len(data)} bytes.")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro inesperado na validação da imagem: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro na validação da imagem.",
            )

    async def handle_image_upload(
        self, image: UploadFile, user_id: int
    ) -> tuple[int, int]:
        try:
            await self._validate_image(image)

            # Salvar arquivo físico (streaming, deduplicado por hash no filesystem)
            file_hash, file_extension = await self.image_dao.save_image(image)

            # Verificar se este usuário já submeteu a mesma imagem antes
            existing_image = await self.image_dao.get_image_by_hash_and_user(
                file_hash, file_extension, user_id
            )

            if existing_image:
                logger.info(
                    f"Usuário ID={user_id} já submeteu imagem ID={existing_image.id}. Criando novo processo."
                )
                process_id = await self.process_service.add_process(existing_image)
                return existing_image.id, process_id

            # Novo registro de imagem para este usuário
            image_data = Image(
                user_id=user_id,
                file_hash=file_hash,
                file_extension=file_extension,
            )
            image_record = await self.image_dao.add_image(image_data)
            logger.info(
                f"Imagem ID={image_record.id} registrada para usuário ID={user_id}."
            )
            process_id = await self.process_service.add_process(image_record)
            return image_record.id, process_id

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao processar upload de imagem: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao processar upload de imagem.",
            )

    async def get_image_by_id(self, image_id: int) -> Image:
        image = await self.image_dao.get_image_by_id(image_id)

        if not image:
            self._handle_image_not_found()

        logger.info(f"Imagem ID={image_id} encontrada.")
        return image

    async def get_all_images_from_user(self, user_id: int) -> list[ImageResponse]:
        images = await self.image_dao.get_all_images_from_user(user_id)
        logger.info(f"{len(images)} imagens encontradas para usuário ID={user_id}.")
        return [ImageResponse.from_orm(image) for image in images]

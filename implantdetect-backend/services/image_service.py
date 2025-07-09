import io
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException, status
from PIL import Image as PILImage, UnidentifiedImageError

from core.logging import get_logger
from daos.image_dao import ImageDAO
from models.entities.image import Image
from core.configuration import settings
from models.dtos.image_dto import ImageResponse, ImageUploadResponse
from services.process_service import ProcessService

logger = get_logger(__name__)

class ImageService:
    def __init__(self, db: AsyncSession):
        self._init_configurations()
        self.image_dao = ImageDAO(db)
        self.process_service = ProcessService(db)
        
    def _handle_image_not_found(self):
        """
        Lida com o caso de imagem não encontrada.
        """
        
        logger.error("Imagem não encontrada.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagem não encontrada."
        )
        
    def _init_configurations(self) -> None:
        """
        Inicializa as configurações do serviço.
        """

        self.image_maximum_size = settings.IMAGE_MAXIMUM_SIZE
        self.image_supported_formats = [f.lower() for f in settings.IMAGE_SUPPORTED_FORMATS]

    def _check_size(self, size: int) -> bool:
        """
        Valida o tamanho da imagem.
        """

        if size > self.image_maximum_size:
            size_mb = size / (1024 * 1024)
            max_size_mb = self.image_maximum_size / (1024 * 1024)
            logger.warning(f"Imagem muito grande: {size_mb:.2f} MB.")
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Imagem muito grande: {size_mb:.2f} MB. Tamanho máximo permitido é {max_size_mb:.2f} MB."
            )
        return True

    def _check_format(self, format: str) -> bool:
        """
        Valida o formato da imagem.
        """

        if format.lower() not in self.image_supported_formats:
            logger.warning(f"Formato de imagem não suportado: {format}")
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Formato de imagem não suportado: {format}. Formatos suportados: {', '.join(self.image_supported_formats)}."
            )
        return True

    async def _validate_image(self, image: UploadFile) -> bool:
        """
        Valida o tamanho e formato da imagem enviada.
        """

        try:
            contents = await image.read()
            self._check_size(len(contents))
            
            img_bytes = io.BytesIO(contents)
            pil_image = PILImage.open(img_bytes)
            if pil_image.format is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de imagem não reconhecido."
                )
                
            self._check_format(pil_image.format)
            
            await image.seek(0)
            
            logger.info(f"Imagem {image.filename} validada com sucesso: "
                         f"{pil_image.size[0]}x{pil_image.size[1]} pixels, "
                         f"formato {pil_image.format}, tamanho {len(contents)} bytes.")
            return True

        except UnidentifiedImageError:
            logger.warning("Falha ao identificar imagem.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arquivo enviado não é uma imagem válida."
            )
            
        except Exception as e:
            logger.error(f"Erro inesperado durante a validação da imagem: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro na validação da imagem: {str(e)}"
            )

    async def handle_image_upload(self, image: UploadFile, user_id: int) -> tuple[int, int]:
        """
        Processa o upload de uma imagem.
        1. Valida a extensão e tamanho
        2. Salva o arquivo no disco (se não existir)
        3. Cria um registro no banco de dados (se não existir)
        4. Adiciona à fila de processamento
        """
        
        try:
            await self._validate_image(image)

            file_hash, file_extension = await self.image_dao.save_image(image)

            existing_image = await self.image_dao.get_image_by_hash(file_hash, file_extension)
            
            if existing_image:
                logger.info(f"Imagem já existe no banco de dados com ID {existing_image.id}.")
                process_id = await self.process_service.add_process(existing_image)
                return existing_image.id, process_id
            
            image_data = Image(
                user_id=user_id,
                file_hash=file_hash,
                file_extension=file_extension,
            )
            
            image_record = await self.image_dao.add_image(image_data)
            logger.info(f"Imagem {image_record.id} salva com sucesso em {file_hash}.")
            process_id = await self.process_service.add_process(image_record)
            return image_record.id, process_id

        except Exception as e:
            logger.error(f"Erro ao processar upload de imagem: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao processar upload de imagem: {str(e)}"
            )

    async def get_image_by_id(self, image_id: int) -> ImageResponse | None:
        """
        Busca uma imagem pelo ID.
        """

        image = await self.image_dao.get_image_by_id(image_id)
        
        if not image:
            self._handle_image_not_found()
        
        logger.info(f"Imagem com ID {image_id} encontrada.")
        return image

    async def get_all_images_from_user(self, user_id: int) -> list[ImageResponse]:
        """
        Busca todas as imagens de um usuário pelo ID.
        """

        images = await self.image_dao.get_all_images_from_user(user_id)
        
        if not images:
            self._handle_image_not_found()
        
        logger.info(f"{len(images)} imagens encontradas para o usuário com ID {user_id}.")
        return [ImageResponse.from_orm(image) for image in images]

    # async def update_image(self, image_id: int, updated_data: dict) -> bool:
    #     """
    #     Atualiza os dados de uma imagem pelo ID.
    #     """

    #     image = await self.get_image_by_id(image_id)
        
    #     if not image:
    #         self._handle_image_not_found()

    #     try:
    #         await self.image_dao.update_image(image_id, updated_data)
    #         logger.info(f"Imagem com ID {image_id} atualizada com sucesso.")
    #         return True
        
    #     except Exception as e:
    #         logger.error(f"Erro ao atualizar imagem com ID {image_id}: {str(e)}")
    #         return False

    # async def remove_image(self, image_id: int) -> bool:
    #     """
    #     Remove uma imagem pelo ID.
    #     """

    #     image = await self.get_image_by_id(image_id)
        
    #     if not image:
    #         self._handle_image_not_found()

    #     try:
    #         await self.image_dao.remove_image(image_id)
            
    #         logger.info(f"Imagem com ID {image_id} removida com sucesso.")
    #         return True

    #     except Exception as e:
    #         logger.error(f"Erro ao remover imagem com ID {image_id}: {str(e)}")
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail=f"Erro ao remover imagem: {str(e)}"
    #         )
import os
import hashlib
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from implantdetect_shared.entities.image import Image
from implantdetect_shared.enums.general_status import GeneralStatus


class ImageDAO:
    def __init__(self, db: AsyncSession, image_repository: str):
        self.db = db
        self.image_repository = image_repository

    async def save_image(self, image: UploadFile) -> tuple[str, str]:
        """Persiste o arquivo físico (deduplica por hash) e retorna (hash, extensão).

        O registro de banco deve ser criado separadamente pelo service para garantir
        que cada usuário tenha seu próprio registro de imagem mesmo para arquivos iguais.
        """
        try:
            assert image.filename is not None, "O nome do arquivo não pode ser nulo."

            file_extension = Path(image.filename).suffix.lower()
            hasher = hashlib.sha256()
            folder = Path(self.image_repository)
            tmp_path = folder / f"tmp_{os.urandom(8).hex()}"

            # Streaming: lê em chunks para evitar carregar o arquivo inteiro em memória
            await image.seek(0)
            with open(tmp_path, "wb") as f:
                while True:
                    chunk = await image.read(65536)
                    if not chunk:
                        break
                    hasher.update(chunk)
                    f.write(chunk)

            file_hash = hasher.hexdigest()
            final_path = folder / f"{file_hash}{file_extension}"

            if final_path.exists():
                # Arquivo já existe fisicamente — descartar temporário
                os.unlink(tmp_path)
            else:
                os.rename(tmp_path, final_path)

            return file_hash, file_extension

        except HTTPException:
            raise
        except Exception:
            if "tmp_path" in dir() and tmp_path.exists():
                os.unlink(tmp_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao salvar a imagem.",
            )

    async def add_image(self, image: Image) -> Image:
        try:
            self.db.add(image)
            await self.db.flush()
            await self.db.refresh(image)
            return image

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao adicionar imagem ao banco de dados.",
            )

    async def get_all_images_from_user(self, user_id: int) -> list[Image]:
        result = await self.db.execute(
            select(Image).filter(
                Image.user_id == user_id, Image.active == GeneralStatus.ACTIVE
            )
        )
        return list(result.scalars().all())

    async def get_image_by_id(self, image_id: int) -> Image | None:
        result = await self.db.execute(select(Image).filter(Image.id == image_id))
        return result.scalars().first()

    async def get_image_by_hash_and_user(
        self, file_hash: str, file_extension: str, user_id: int
    ) -> Image | None:
        """Busca imagem de um usuário específico pelo hash — usado para deduplicação por usuário."""
        result = await self.db.execute(
            select(Image).filter(
                Image.file_hash == file_hash,
                Image.file_extension == file_extension,
                Image.user_id == user_id,
            )
        )
        return result.scalars().first()

    async def user_has_access_to_hash(self, file_hash: str, user_id: int) -> bool:
        """Verifica se o usuário tem pelo menos uma imagem com esse hash (para autorizar download)."""
        result = await self.db.execute(
            select(Image.id)
            .filter(
                Image.file_hash == file_hash,
                Image.user_id == user_id,
            )
            .limit(1)
        )
        return result.scalar() is not None

import os
import uvicorn

from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse, FileResponse
from fastapi import FastAPI, Request, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.logging import get_logger
from core.configuration import settings
from models.dtos.result_dto import Result
from controllers import user_controller, image_controller, process_controller
from core.database import create_tables, database_health_check
from services.queue_service import queue_service
from fastapi.middleware.cors import CORSMiddleware

logger = get_logger(__name__)

os.makedirs(settings.IMAGE_REPOSITORY, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_tables()
    logger.info("Banco de dados inicializado")
    await queue_service.connect()
    yield
    # Shutdown
    await queue_service.disconnect()
    logger.info("Aplicativo encerrando, liberando recursos")


docs_enabled = settings.ENVIRONMENT != "production"

app = FastAPI(
    title="ImplantDetect API",
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
    openapi_url="/openapi.json" if docs_enabled else None,
    version="1.0.0",
    root_path="/api",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_controller.router, prefix="/users", tags=["users"])
app.include_router(image_controller.router, prefix="/images", tags=["images"])
app.include_router(process_controller.router, prefix="/processing", tags=["processing"])


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code, content=Result.error(message=exc.detail)
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content=Result.error(message=str(exc)))


@app.get("/health", tags=["health"])
async def health_check():
    """Healthcheck da aplicação e do banco de dados."""

    try:
        db_status = await database_health_check()
    except Exception as e:
        logger.error(f"Erro no healthcheck do banco: {e}")
        db_status = "unavailable"

    return {"status": "ok", "database": db_status}


@app.get("/uploads/{file_hash}", tags=["uploads"])
async def get_protected_image(file_hash: str):
    file_path = os.path.join("uploads", file_hash)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return FileResponse(file_path)


if __name__ == "__main__":
    logger.info("Inicializando o backend do ImplantDetect...")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

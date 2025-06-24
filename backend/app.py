import os
import uvicorn
import logging

from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse, FileResponse
from fastapi import FastAPI, Request, Depends, HTTPException, status
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.configuration import settings
from models.dtos.result_dto import Result
from core.security import get_current_user
from core.database import create_tables, database_health_check
from controllers import user_controller, image_controller, queue_controller

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

os.makedirs("logs", exist_ok=True)
os.makedirs(settings.IMAGE_REPOSITORY, exist_ok=True)

# Verificar o modo da fila
logger.info(f"Tentando usar Beanstalkd em {settings.BEANSTALK_HOST}:{settings.BEANSTALK_PORT}")

is_production = os.getenv("ENVIRONMENT") == "production"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_tables()
    logger.info("Banco de dados inicializado")
    yield
    # Shutdown
    logger.info("Aplicativo encerrando, liberando recursos")

app = FastAPI(
    title="ImplantDetect API",
    docs_url="/docs" if not is_production else None,
    redoc_url="/redoc" if not is_production else None,
    openapi_url="/openapi.json" if not is_production else None,
    version="1.0.0",
    root_path="/api",
    lifespan=lifespan
)

app.include_router(user_controller.router, prefix="/users", tags=["users"])
app.include_router(image_controller.router, prefix="/images", tags=["images"])
app.include_router(queue_controller.router, prefix="/queue", tags=["queue"])

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=Result.error(message=exc.detail)
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=Result.error(message=str(exc))
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=Result.error(message=str(exc))
    )
    
@app.get("/health", tags=["health"])
async def health_check():
    """Healthcheck da aplicação e do banco de dados."""
    
    try:
        db_status = await database_health_check()
    except Exception as e:
        logger.error(f"Erro no healthcheck do banco: {e}")
        db_status = "unavailable"
    
    queue_mode = "memory" if settings.FORCE_MEMORY_QUEUE else "beanstalkd"
        
    return {"status": "ok", "database": db_status, "queue": queue_mode}

@app.get("/uploads/{filename}", tags=["images"])
async def get_protected_image(filename: str, user=Depends(get_current_user)):
    file_path = os.path.join("uploads", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return FileResponse(file_path)

if __name__ == "__main__":
    logger.info("Inicializando o backend do ImplantDetect...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
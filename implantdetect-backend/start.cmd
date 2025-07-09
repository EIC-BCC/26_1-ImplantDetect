@echo off
echo Parando containers existentes...

echo Iniciando API e PostgreSQL com Docker Compose...

echo Verificando se o Docker existe no sistema...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Docker nao esta instalado ou rodando!
    pause
    exit /b 1
)

echo Verificando se o Docker Desktop Linux Engine esta rodando...
docker info >nul 2>&1
if errorlevel 1 (
    echo ERRO: Docker Desktop Linux Engine nao esta rodando!
    echo Certifique-se de que o Docker Desktop esta iniciado.
    pause
    exit /b 1
)

REM Criar pastas necessárias se não existirem
if not exist uploads mkdir uploads
if not exist logs mkdir logs

docker-compose down

docker-compose up --build

echo =============================================================
echo Verificando se os containers estao em execucao...
docker ps | findstr "implantdetect-backend" >nul 2>&1
if errorlevel 1 (
    echo ERRO: Os containers nao estao em execucao!
    echo Finalizando o script, verifique os logs para mais detalhes.
    pause
    exit /b 1
)
echo Servicos em execucao:
echo - API: http://localhost:8000
echo - PostgreSQL: localhost:5432
echo =============================================================


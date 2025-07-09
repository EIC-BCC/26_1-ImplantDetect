@echo off
REM Script para iniciar apenas o PostgreSQL com Docker Compose
echo ============================================================
echo ImplantDetect - Iniciando PostgreSQL
echo ============================================================

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

echo Parando container PostgreSQL existente se houver...
docker-compose stop postgres >nul 2>&1

echo Iniciando PostgreSQL com Docker Compose...
docker-compose up -d postgres

if errorlevel 0 (
    echo.
    echo ============================================================
    echo PostgreSQL iniciado com sucesso!
    echo Aguardando PostgreSQL ficar pronto...
    timeout /t 5 /nobreak >nul
    
    echo Verificando status do container...
    docker-compose ps postgres
    
    echo.
    echo Para parar: docker-compose stop postgres
    echo Para logs: docker-compose logs -f postgres
    echo ============================================================
) else (
    echo.
    echo ERRO: Falha ao iniciar PostgreSQL!
    echo Verifique os logs: docker-compose logs postgres
    pause
)

echo.
echo Pressione qualquer tecla para sair...
pause >nul
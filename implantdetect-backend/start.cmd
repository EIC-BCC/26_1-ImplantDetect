@echo off
echo Parando containers existentes...

echo Iniciando API e PostgreSQL com Docker Compose...

REM Criar pastas necessárias se não existirem
if not exist uploads mkdir uploads
if not exist logs mkdir logs

docker-compose down

docker-compose up --build

echo =============================================================
echo Servicos em execucao:
echo - API: http://localhost:8000
echo - PostgreSQL: localhost:5432
echo =============================================================

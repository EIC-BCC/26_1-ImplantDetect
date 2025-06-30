#!/bin/bash
# Script para iniciar o backend com opções de fila

echo "============================================================="
echo "ImplantDetect --> Backend (API)"
echo "============================================================="
echo "Iniciando API..."
echo "Ctrl+C para encerrar"
echo "============================================================="

python -m uvicorn app:app --reload

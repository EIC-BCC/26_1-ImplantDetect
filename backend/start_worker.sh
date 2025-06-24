#!/bin/bash
# Script para iniciar o worker

echo "============================================================="
echo "ImplantDetect --> Worker (Beanstalkd)"
echo "============================================================="
echo "Iniciando Worker..."
echo "Ctrl+C para encerrar"
echo "============================================================="

python workers/run_worker.py --loglevel=info --concurrency=1

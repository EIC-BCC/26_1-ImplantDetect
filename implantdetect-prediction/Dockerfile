FROM pytorch/pytorch:2.7.1-cuda12.8-cudnn9-runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgl1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV YOLO_CONFIG_DIR=/app/.ultralytics

WORKDIR /app

COPY implantdetect-shared/ /app/shared/
RUN pip install --no-cache-dir /app/shared

COPY implantdetect-prediction/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY implantdetect-prediction/ /app/

RUN adduser -u 5678 --disabled-password --gecos "" appuser && \
    chown -R appuser /app && \
    mkdir -p /app/uploads /app/logs /app/.ultralytics && \
    chown -R appuser:appuser /app/uploads /app/logs /app/.ultralytics

USER appuser

CMD ["python", "main.py"]

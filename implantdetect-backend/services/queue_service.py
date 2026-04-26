import aio_pika
from aio_pika import DeliveryMode, Message

from core.configuration import settings
from core.logging import get_logger
from implantdetect_shared.schemas.queue_message import PredictionRequest

logger = get_logger(__name__)

PREDICTION_QUEUE = "prediction_requests"


class QueueService:
    def __init__(self):
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None

    async def connect(self):
        self._connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        self._channel = await self._connection.channel()
        await self._channel.declare_queue(PREDICTION_QUEUE, durable=True)
        logger.info("Conectado ao RabbitMQ")

    async def disconnect(self):
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
        logger.info("Desconectado do RabbitMQ")

    async def publish_prediction_request(
        self, process_id: int, file_hash: str, file_extension: str
    ):
        if not self._channel:
            raise RuntimeError("QueueService não conectado ao RabbitMQ")

        payload = (
            PredictionRequest(
                process_id=process_id,
                file_hash=file_hash,
                file_extension=file_extension,
            )
            .model_dump_json()
            .encode()
        )

        await self._channel.default_exchange.publish(
            Message(body=payload, delivery_mode=DeliveryMode.PERSISTENT),
            routing_key=PREDICTION_QUEUE,
        )
        logger.info(f"Requisição de predição enfileirada para o processo {process_id}")


queue_service = QueueService()

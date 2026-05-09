import asyncio
import signal

import aio_pika
from aio_pika import IncomingMessage

from core.configuration import settings
from core.database import async_session_factory
from core.logging import get_logger, setup_logging
from implantdetect_shared.daos.label_dao import LabelDao
from implantdetect_shared.daos.process_dao import ProcessDao
from implantdetect_shared.entities.process_results import ProcessResults
from implantdetect_shared.enums.process_status import ProcessStatus
from implantdetect_shared.schemas.queue_message import PredictionRequest
from wrapper.yolo_wrapper import YoloWrapper

setup_logging()
logger = get_logger(__name__)

PREDICTION_QUEUE = "prediction_requests"

yolo = YoloWrapper()


async def handle_message(message: IncomingMessage):
    async with message.process(requeue=False):
        request = PredictionRequest.model_validate_json(message.body)

        logger.info(f"Processando mensagem para processo {request.process_id}")

        async with async_session_factory() as session:
            process_dao = ProcessDao(session)
            label_dao = LabelDao(session)

            try:
                await process_dao.update_process_status(
                    request.process_id, ProcessStatus.RUNNING
                )
                await session.commit()

                predictions = await yolo.predict(
                    request.file_hash, request.file_extension
                )

                for prediction in predictions:
                    label = await label_dao.get_label_by_name(prediction.class_name)
                    bb = prediction.bounding_box
                    result = ProcessResults(
                        process_id=request.process_id,
                        class_id=label.id if label else None,
                        confidence=prediction.confidence,
                        bb_x1_center=bb["x1"],
                        bb_y1_center=bb["y1"],
                        bb_x2_center=bb["x2"],
                        bb_y2_center=bb["y2"],
                        bb_x3_center=bb["x3"],
                        bb_y3_center=bb["y3"],
                        bb_x4_center=bb["x4"],
                        bb_y4_center=bb["y4"],
                    )
                    await process_dao.add_process_result(result)

                await process_dao.update_process_status(
                    request.process_id, ProcessStatus.COMPLETED
                )
                await session.commit()
                logger.info(
                    f"Processo {request.process_id} concluído com {len(predictions)} predições."
                )

            except Exception as e:
                await session.rollback()
                logger.error(
                    f"Erro ao processar processo {request.process_id}: {e}",
                    exc_info=True,
                )
                try:
                    await process_dao.update_process_status(
                        request.process_id, ProcessStatus.FAILED
                    )
                    await process_dao.add_process_result(
                        ProcessResults(process_id=request.process_id, message=str(e))
                    )
                    await session.commit()
                except Exception as inner_e:
                    await session.rollback()
                    logger.error(
                        f"Falha ao registrar erro do processo {request.process_id}: {inner_e}",
                        exc_info=True,
                    )


async def main():
    stop_event = asyncio.Event()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop_event.set)

    logger.info(f"Conectando ao RabbitMQ em {settings.RABBITMQ_URL}...")
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(
            prefetch_count=1
        )  # one message at a time: YOLO inference is GPU/CPU-bound
        queue = await channel.declare_queue(PREDICTION_QUEUE, durable=True)

        await queue.consume(handle_message)
        logger.info("Worker aguardando mensagens de predição...")

        await stop_event.wait()

    logger.info("Worker encerrado.")


if __name__ == "__main__":
    asyncio.run(main())

# app/streaming/consumer.py
import json
import logging
from aiokafka import AIOKafkaConsumer
from app.core.config import settings
from app.service.orchestrator import orchestrator  # Импортируем сервис

logger = logging.getLogger(__name__)


class TrafficConsumer:
    def __init__(self):
        self.consumer = None

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            settings.KAFKA_TOPIC_SUSPICIOUS,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_CONSUMER_GROUP,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            auto_offset_reset="earliest"
        )
        await self.consumer.start()

        try:
            async for msg in self.consumer:
                # Этот принт сработает ВСЕГДА, когда байты долетели до кода
                print(f"\n[DEBUG] Сообщение пришло! Value: {msg.value}")
                await orchestrator.process_new_flow(msg.value)
        except Exception as e:
            # Если тут будет ошибка — мы её УВИДИМ
            print(f"\n[CRITICAL ERROR] Ошибка в цикле консьюмера: {str(e)}")
            logger.error(f"❌ Ошибка в аналитическом цикле: {e}")

    async def stop(self):
        if self.consumer:
            await self.consumer.stop()


traffic_consumer = TrafficConsumer()
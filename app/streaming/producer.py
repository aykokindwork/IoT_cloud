# app/streaming/producer.py
import json
import logging
from aiokafka import AIOKafkaProducer
from app.core.config import settings

logger = logging.getLogger(__name__)


class CommandProducer:
    def __init__(self):
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self.producer.start()
        logger.info("🚀 Command Producer (Feedback Loop) запущен")

    async def send_verdict(self, flow_id: str, label: str, ip: str):
        if not self.producer:
            logger.error("❌ Продюсер не запущен!")
            return

        verdict_msg = {
            "flow_id": flow_id,
            "verdict": label,
            "ip": ip
        }

        try:
            # Используем топик из настроек
            await self.producer.send_and_wait(settings.KAFKA_TOPIC_VERDICT, verdict_msg)
            logger.warning(f"⚡ Команда блокировки отправлена: {ip} ({label})")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки в Kafka: {e}")

    async def stop(self):
        if self.producer:
            await self.producer.stop()
            logger.info("🛑 Command Producer остановлен")


# Создаем синглтон
command_producer = CommandProducer()
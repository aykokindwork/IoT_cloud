# app/streaming/consumer.py
import json
import logging
import asyncio
from datetime import datetime
from aiokafka import AIOKafkaConsumer
from app.core.config import settings
from app.ml.classifier import classifier
from app.storage.mongo import db_manager

logger = logging.getLogger(__name__)


class TrafficConsumer:
    def __init__(self):
        self.consumer = None

    async def start(self):
        """Запуск консьюмера с механизмом повторных попыток подключения"""
        logger.info(f"📡 Подключение к Kafka на {settings.KAFKA_BOOTSTRAP_SERVERS}...")

        # Настраиваем консьюмер
        self.consumer = AIOKafkaConsumer(
            settings.KAFKA_TOPIC_SUSPICIOUS,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_CONSUMER_GROUP,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            auto_offset_reset="earliest"
        )

        # Пытаемся запустить консьюмер (ждем, пока Кафка в докере прогреется)
        for attempt in range(15):
            try:
                await self.consumer.start()
                logger.info(f"✅ Kafka Consumer успешно запущен. Слушаем топик: {settings.KAFKA_TOPIC_SUSPICIOUS}")
                break
            except Exception as e:
                logger.warning(f"⏳ Ожидание Kafka (попытка {attempt + 1}/15)... Ошибка: {e}")
                await asyncio.sleep(5)
        else:
            logger.error("❌ Не удалось запустить Kafka Consumer после 15 попыток.")
            return

        try:
            async for msg in self.consumer:
                payload = msg.value
                logger.info(f"📥 Получен пакет на анализ...")

                # 1. Предсказание нейронкой
                label, confidence = classifier.predict(payload)
                logger.info(f"🤖 Вердикт: {label} (уверенность: {confidence:.2%})")

                # 2. Сохранение в базу
                log_entry = {
                    "timestamp": datetime.utcnow(),
                    "prediction": label,
                    "confidence": confidence,
                    "features": payload
                }

                try:
                    await db_manager.db["analysis_logs"].insert_one(log_entry)
                    logger.info("💾 Результат сохранен в MongoDB")
                except Exception as e:
                    logger.error(f"❌ Ошибка записи в MongoDB: {e}")

        except Exception as e:
            logger.error(f"❌ Критическая ошибка в цикле чтения Kafka: {e}")
        finally:
            await self.stop()

    async def stop(self):
        if self.consumer:
            await self.consumer.stop()
            logger.info("🛑 Kafka Consumer остановлен.")


traffic_consumer = TrafficConsumer()
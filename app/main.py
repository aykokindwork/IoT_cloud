# app/main.py
import asyncio
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.storage.mongo import connect_to_mongo, close_mongo_connection
from app.streaming.consumer import traffic_consumer
from app.ml.classifier import classifier  # Импортируем наш синглтон модели

# Настраиваем логирование, чтобы видеть отчет о загрузке в терминале
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- ЭТАП ЗАПУСКА (STARTUP) ---
    logger.info("🚀 Инициализация IoT Cloud сервиса...")

    # 1. Подключаемся к базе данных
    await connect_to_mongo()

    # 2. Загружаем нейросеть в оперативную память
    # Если тут будет ошибка (например, файл не найден), сервер упадет СРАЗУ.
    # Это правильно: лучше не запуститься вообще, чем работать со сломанными мозгами.
    classifier.load_model()

    # 3. Запускаем Kafka-поток в фоновом режиме
    kafka_task = asyncio.create_task(traffic_consumer.start())

    yield  # В этой точке сервер начинает принимать запросы (например, /health)

    # --- ЭТАП ОСТАНОВКИ (SHUTDOWN) ---
    logger.info("📉 Завершение работы сервиса...")
    kafka_task.cancel()
    await traffic_consumer.stop()
    await close_mongo_connection()


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "model_loaded": classifier.model is not None
    }
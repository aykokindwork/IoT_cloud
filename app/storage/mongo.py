# app/storage/mongo.py
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

# Глобальный объект для работы с базой
db_manager = MongoDB()

async def connect_to_mongo():
    logger.info("Подключаемся к MongoDB...")
    db_manager.client = AsyncIOMotorClient(settings.MONGO_URI)
    db_manager.db = db_manager.client[settings.MONGO_DB_NAME]
    logger.info(f"✅ База данных подключена: {settings.MONGO_DB_NAME}")

async def close_mongo_connection():
    logger.info("Закрываем соединение с MongoDB...")
    if db_manager.client:
        db_manager.client.close()
        logger.info("🛑 Соединение закрыто.")
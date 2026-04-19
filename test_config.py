# test_config.py
from app.core.config import settings

print("=== ПРОВЕРКА КОНФИГА ===")
print(f"🔥 Проект: {settings.PROJECT_NAME}")
print(f"📡 Kafka слушает на: {settings.KAFKA_BOOTSTRAP_SERVERS}")
print(f"🗄️ База данных: {settings.MONGO_URI}")
print(f"🧠 Модель ищет файлы по пути: {settings.MODEL_PATH}")
print("========================")
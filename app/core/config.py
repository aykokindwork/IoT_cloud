# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Базовые настройки
    PROJECT_NAME: str = "IoT Cloud IDS"

    # Kafka
    # Обрати внимание: тут нет типа "= значение".
    # Это значит Pydantic ОБЯЗАН найти это в .env файле.
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_TOPIC_SUSPICIOUS: str = "suspicious_traffic"
    KAFKA_CONSUMER_GROUP: str = "cloud_lstm_group"

    # MongoDB
    MONGO_URI: str
    MONGO_DB_NAME: str = "iot_logs"

    # Пути к файлам модели друга
    MODEL_PATH: str = "models/iot_ids_model.h5"
    SCALER_PATH: str = "models/scaler.pkl"
    ENCODER_PATH: str = "models/label_encoder.pkl"
    FEATURES_PATH: str = "models/feature_columns.json"

    # Указываем, откуда читать переменные
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Создаем единственный экземпляр настроек (Singleton).
settings = Settings()
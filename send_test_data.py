# send_test_data.py
import json
import random
from kafka import KafkaProducer

# Настройки (те же, что в .env)
KAFKA_SERVER = '192.168.1.10:9092' # Укажи свой IP
TOPIC = 'suspicious-flows'

# 1. Загружаем названия признаков, чтобы не ошибиться
with open('models/feature_columns.json', 'r') as f:
    features = json.load(f)

# 2. Создаем фейковые данные (имитация одного сетевого потока)
fake_data = {feat: random.uniform(0, 100) for feat in features}

# 3. Отправляем в Kafka
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_SERVER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print(f"🚀 Отправка тестового пакета в топик {TOPIC}...")
producer.send(TOPIC, fake_data)
producer.flush()
print("✅ Пакет отправлен!")
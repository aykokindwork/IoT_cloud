# app/ml/classifier.py
import logging
import numpy as np
import joblib
import tensorflow as tf
import json
from app.core.config import settings
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

logger = logging.getLogger(__name__)


class IDSClassifier:  # Переименовал для точности
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.features = None

    def load_model(self):
        try:
            logger.info(f"🧠 Загрузка FFNN модели: {settings.MODEL_PATH}")
            self.model = tf.keras.models.load_model(settings.MODEL_PATH)
            self.scaler = joblib.load(settings.SCALER_PATH)
            self.label_encoder = joblib.load(settings.ENCODER_PATH)

            with open(settings.FEATURES_PATH, 'r') as f:
                self.features = json.load(f)

            logger.info(f"✅ Модель загружена. Классов для распознавания: {len(self.label_encoder.classes_)}")
        except Exception as e:
            logger.error(f"❌ Ошибка при загрузке модели: {e}")
            raise e

    def predict(self, data: dict):
        try:
            # 1. Извлекаем список признаков, который подготовил Go
            input_features = data.get("features")

            if not input_features or len(input_features) != len(self.features):
                logger.error(
                    f"❌ Некорректное кол-во признаков: получено {len(input_features) if input_features else 0}, ждали {len(self.features)}")
                return "Error", 0.0

            # 2. Превращаем в массив numpy (1, 46)
            input_array = np.array(input_features).reshape(1, -1)

            # 3. Нормализация (Scaler)
            scaled_data = self.scaler.transform(input_array)

            # 4. Предсказание
            prediction = self.model.predict(scaled_data, verbose=0)

            print(f"DEBUG: Raw prediction probabilities: {prediction[0]}")

            class_idx = np.argmax(prediction)
            label = self.label_encoder.inverse_transform([class_idx])[0]
            confidence = float(np.max(prediction))

            return label, confidence
        except Exception as e:
            logger.error(f"❌ Ошибка классификации: {e}")
            return "Error", 0.0


classifier = IDSClassifier()
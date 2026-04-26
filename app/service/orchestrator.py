# app/services/orchestrator.py
import logging
from datetime import datetime
from app.ml.classifier import classifier
from app.storage.mongo import db_manager
from app.streaming.producer import command_producer

logger = logging.getLogger(__name__)


class DetectionOrchestrator:
    def __init__(self):
        pass

    @staticmethod
    async def process_new_flow(payload: dict):
        """
        Главный пайплайн обработки одного сетевого потока.
        """
        flow_id = payload.get("flow_id", "unknown")

        # 1. Получаем вердикт от нейронки
        # Мы не паримся о том, как она работает, просто вызываем интерфейс
        label, confidence = classifier.predict(payload)
        logger.info(f"🔍 [Orchestrator] Flow {flow_id} analyzed: {label} ({confidence:.2%})")

        # 2. Feedback Loop: если это не чистый трафик, отдаем приказ на Edge
        if label != "BenignTraffic":
            target_ip = flow_id.split(':')[0] if ':' in flow_id else flow_id
            await command_producer.send_verdict(flow_id, label, target_ip)

        # 3. Persistence: сохраняем историю в MongoDB
        await db_manager.db["analysis_logs"].insert_one({
            "timestamp": datetime.utcnow(),
            "flow_id": flow_id,
            "prediction": label,
            "confidence": confidence,
            "features": payload
        })
        logger.debug(f"💾 [Orchestrator] Incident saved to DB")


# Создаем объект для импорта
orchestrator = DetectionOrchestrator()
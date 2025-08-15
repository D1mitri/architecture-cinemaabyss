from confluent_kafka import Producer
import json
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class EventProducer:
    def __init__(self, kafka_broker: str):
        self._producer = Producer({
            'bootstrap.servers': kafka_broker,
            'message.max.bytes': 5242880,
            'queue.buffering.max.ms': 100
        })

    def produce_event(self, topic: str, event_type: str, data: Dict[str, Any]):
        """Отправка события в Kafka"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

        try:
            self._producer.produce(
                topic=topic,
                value=json.dumps(event).encode('utf-8'),
                callback=self._delivery_report
            )
            self._producer.flush(timeout=1.0)
            logger.info(f"Produced {event_type} event to {topic}")
        except Exception as e:
            logger.error(f"Failed to produce event: {str(e)}")
            raise

    @staticmethod
    def _delivery_report(err, msg):
        """Callback для обработки статуса доставки"""
        if err:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

_producer_instance = None

def get_producer() -> EventProducer:
    """Фабрика для получения продюсера"""
    global _producer_instance
    if _producer_instance is None:
        kafka_broker = "kafka:9092"
        _producer_instance = EventProducer(kafka_broker)
    return _producer_instance
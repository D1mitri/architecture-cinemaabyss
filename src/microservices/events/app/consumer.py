from confluent_kafka import Consumer, KafkaException
import json
import logging
from .models.schemas import MovieEvent, UserInput, PaymentInput

logger = logging.getLogger(__name__)

class EventProcessor:
    def __init__(self):
        self.consumer = Consumer({
            'bootstrap.servers': 'kafka:9092',
            'group.id': 'events-processor',
            'auto.offset.reset': 'earliest'
        })
        self.consumer.subscribe(['movie_events', 'user_events', 'payment_events'])

    def process_events(self):
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    raise KafkaException(msg.error())

                try:
                    event = json.loads(msg.value().decode('utf-8'))
                    if msg.topic() == 'movie_events':
                        self.process_movie_event(event['data'])
                    elif msg.topic() == 'user_events':
                        self.process_user_event(event['data'])
                    elif msg.topic() == 'payment_events':
                        self.process_payment_event(event['data'])
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

    @staticmethod
    def process_movie_event(event_data: dict):
        try:
            event = MovieEvent(**event_data)
            logger.info(f"Processed movie event: {event}")
        except Exception as e:
            logger.error(f"Invalid movie event: {e}")

    @staticmethod
    def process_user_event(event_data: dict):
        try:
            event = UserInput(**event_data)
            logger.info(f"Processed user event: {event}")
        except Exception as e:
            logger.error(f"Invalid user event: {e}")

    @staticmethod
    def process_payment_event(event_data: dict):
        try:
            event = PaymentInput(**event_data)
            logger.info(f"Processed payment event: {event}")
        except Exception as e:
            logger.error(f"Invalid payment event: {e}")
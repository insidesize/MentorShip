import json
from typing import Optional
from aiokafka import AIOKafkaProducer
from app.settings import KAFKA_BROKERS, KAFKA_TOPIC

class KafkaProducer:
    def __init__(self):
        self.producer: Optional[AIOKafkaProducer] = None

    async def init(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BROKERS
        )
        try:
            await self.producer.start()
        except Exception as e:
            await self.close()
            raise RuntimeError(f"Failed to start Kafka producer: {e}")

    async def close(self):
        if self.producer:
            try:
                await self.producer.stop()
            except Exception as e:
                raise RuntimeError(f"Failed to stop Kafka producer: {e}")

    async def send(self, search_query):
        message = json.dumps(search_query).encode("utf-8")
        try:
            await self.producer.send_and_wait(KAFKA_TOPIC, message)
            print(f"Sent message: {message}")
        except Exception as e:
            raise RuntimeError(f"Error sending message to Kafka: {e}")

    async def check_health(self):
        return self.producer is not None and not self.producer._closed

# Экземпляр продюсера
kafka_producer = KafkaProducer()

# Глобальная функция, которую ты импортируешь в main.py
async def send_search_task(search_query):
    await kafka_producer.send(search_query)
import os


KAFKA_BROKERS = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "search_topic")
RESPONSE_TOPIC = "response_topic"
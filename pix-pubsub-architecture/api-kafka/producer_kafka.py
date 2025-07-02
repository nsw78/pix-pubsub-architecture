from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers='kafka-service:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def publish_event(topic, value):
    producer.send(topic, value)
    producer.flush()

import pika
import json

def publish_event(routing_key, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq-service'))
    channel = connection.channel()
    channel.exchange_declare(exchange='pix', exchange_type='topic', durable=True)
    channel.basic_publish(exchange='pix', routing_key=routing_key, body=json.dumps(message))
    connection.close()

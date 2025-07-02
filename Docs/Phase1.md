Guia detalhado com código:

---

### 📁 **1. Estrutura inicial do projeto**

Crie os diretórios com este comando:

```bash
mkdir -p pix-pubsub-architecture/{api-kafka,api-rabbitmq,k8s/{kafka,rabbitmq,api-kafka,api-rabbitmq,ingress,monitoring},docker}
cd pix-pubsub-architecture
```

---

### 📄 **2. .gitignore**

```gitignore
__pycache__/
*.pyc
.env
*.log
.DS_Store
*.db
.idea/
.vscode/
```

---

### 📄 **3. requirements.txt**

```txt
flask
kafka-python
pika
```

---

### 🐍 **4. API Kafka: `api-kafka/app.py`**

```python
from flask import Flask, request, jsonify
from producer_kafka import publish_event

app = Flask(__name__)

@app.route("/pix/kafka", methods=["POST"])
def pix_kafka():
    data = request.json
    topic = data.get("topic", "pix.payment.requested")
    publish_event(topic, data)
    return jsonify({"status": "Event sent to Kafka", "topic": topic}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

---

### 🐍 **5. API Kafka: `api-kafka/producer_kafka.py`**

```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers='kafka-service:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def publish_event(topic, value):
    producer.send(topic, value)
    producer.flush()
```

---

### 🐋 **6. Dockerfile da `api-kafka`**

```Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir flask kafka-python
EXPOSE 5000
CMD ["python", "app.py"]
```

---

### 🐍 **7. API RabbitMQ: `api-rabbitmq/app.py`**

```python
from flask import Flask, request, jsonify
from producer_rabbit import publish_event

app = Flask(__name__)

@app.route("/pix/rabbit", methods=["POST"])
def pix_rabbit():
    data = request.json
    routing_key = data.get("topic", "pix.payment.requested")
    publish_event(routing_key, data)
    return jsonify({"status": "Event sent to RabbitMQ", "routing_key": routing_key}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
```

---

### 🐍 **8. API RabbitMQ: `api-rabbitmq/producer_rabbit.py`**

```python
import pika
import json

def publish_event(routing_key, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq-service'))
    channel = connection.channel()
    channel.exchange_declare(exchange='pix', exchange_type='topic', durable=True)
    channel.basic_publish(exchange='pix', routing_key=routing_key, body=json.dumps(message))
    connection.close()
```

---

### 🐋 **9. Dockerfile da `api-rabbitmq`**

```Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir flask pika
EXPOSE 5001
CMD ["python", "app.py"]
```

---



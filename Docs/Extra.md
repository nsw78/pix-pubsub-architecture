Vou detalhar cada um desses itens para evoluir seu projeto PIX Pub/Sub no Kubernetes.

---

# 1️⃣ CI/CD com GitHub Actions

Vou criar um workflow básico para:

* Buildar as imagens Docker dentro do Minikube (usando docker-in-docker)
* Aplicar os manifests Kubernetes
* Fazer deploy automático ao push na branch `main`

**`.github/workflows/deploy.yml`**

```yaml
name: CI/CD Pipeline

on:
  push:
    branches:
      - main

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to DockerHub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push api-kafka image
        run: |
          docker build -t ${{ secrets.DOCKER_USERNAME }}/api-kafka:latest ./api-kafka
          docker push ${{ secrets.DOCKER_USERNAME }}/api-kafka:latest

      - name: Build and push api-rabbitmq image
        run: |
          docker build -t ${{ secrets.DOCKER_USERNAME }}/api-rabbitmq:latest ./api-rabbitmq
          docker push ${{ secrets.DOCKER_USERNAME }}/api-rabbitmq:latest

      - name: Set up kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'latest'

      - name: Configure kubeconfig
        run: |
          echo "${{ secrets.KUBE_CONFIG_DATA }}" | base64 --decode > $HOME/.kube/config

      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f k8s/namespaces.yaml
          kubectl apply -f k8s/kafka/
          kubectl apply -f k8s/rabbitmq/
          kubectl apply -f k8s/api-kafka/
          kubectl apply -f k8s/api-rabbitmq/
          kubectl apply -f k8s/ingress/
          kubectl apply -f k8s/monitoring/
```

> **Nota:**
>
> * Configure os segredos no GitHub (`DOCKER_USERNAME`, `DOCKER_PASSWORD`, `KUBE_CONFIG_DATA` com o conteúdo do seu kubeconfig base64).
> * Você pode usar GitHub Packages ou outro registry se preferir.

---

# 2️⃣ OpenTelemetry (Tracing Distribuído)

### Como adicionar tracing básico nas APIs com OpenTelemetry

Instale libs extras:

```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-flask opentelemetry-exporter-otlp
```

### Exemplo de instrumentação em `api-kafka/app.py`

```python
from flask import Flask, request, jsonify
from producer_kafka import publish_event

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

app = Flask(__name__)

# Setup OpenTelemetry Tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

FlaskInstrumentor().instrument_app(app)

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

### Otel Collector - Kubernetes Manifest (exemplo simples)

`k8s/monitoring/otel-collector.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: otel-collector
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: otel-collector
  template:
    metadata:
      labels:
        app: otel-collector
    spec:
      containers:
        - name: otel-collector
          image: otel/opentelemetry-collector-contrib:latest
          command:
            - "/otelcontribcol"
            - "--config=/conf/otel-collector-config.yaml"
          volumeMounts:
            - name: config-volume
              mountPath: /conf
      volumes:
        - name: config-volume
          configMap:
            name: otel-collector-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
  namespace: monitoring
data:
  otel-collector-config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
          http:

    exporters:
      logging:
        logLevel: debug
      prometheus:
        endpoint: "0.0.0.0:8888"

    processors:
      batch:

    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [batch]
          exporters: [logging]
        metrics:
          receivers: [otlp]
          processors: [batch]
          exporters: [prometheus]
---
apiVersion: v1
kind: Service
metadata:
  name: otel-collector
  namespace: monitoring
spec:
  selector:
    app: otel-collector
  ports:
    - port: 4317
      name: otlp-grpc
    - port: 55681
      name: otlp-http
```

---

# 3️⃣ Recebimento de mensagens (Consumers)

### Exemplo básico consumer Kafka (crie `api-kafka/consumer_kafka.py`)

```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'pix.payment.requested',
    bootstrap_servers='kafka-service:9092',
    auto_offset_reset='earliest',
    group_id='pix-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

for message in consumer:
    print(f"Received message: {message.value}")
    # Aqui você pode processar a mensagem e chamar outras APIs, armazenar logs, etc.
```

---

### Exemplo básico consumer RabbitMQ (`api-rabbitmq/consumer_rabbit.py`)

```python
import pika
import json

def callback(ch, method, properties, body):
    print(f"Received {method.routing_key}: {body}")
    # Aqui você pode processar a mensagem

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq-service'))
channel = connection.channel()
channel.exchange_declare(exchange='pix', exchange_type='topic', durable=True)

result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

# Bind para todos os tópicos PIX
routing_keys = [
    'pix.payment.requested',
    'pix.payment.validated',
    'pix.payment.settled',
    'pix.notification.sent',
    'pix.audit.log'
]

for key in routing_keys:
    channel.queue_bind(exchange='pix', queue=queue_name, routing_key=key)

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
print('Waiting for messages...')
channel.start_consuming()
```

---

# 4️⃣ Simulador PIX com mock end-to-end

### Script simples que gera eventos na API Kafka e RabbitMQ

`simulator/send_events.py`

```python
import requests
import time
import random

KAFKA_URL = "http://pix.local/kafka"
RABBIT_URL = "http://pix.local/rabbit"

pix_events = [
    {
        "topic": "pix.payment.requested",
        "value": {"transactionId": "tx123", "amount": 100, "payer": "Alice", "receiver": "Bob"}
    },
    {
        "topic": "pix.payment.validated",
        "value": {"transactionId": "tx123", "status": "validated"}
    },
    {
        "topic": "pix.payment.settled",
        "value": {"transactionId": "tx123", "status": "settled"}
    },
    {
        "topic": "pix.notification.sent",
        "value": {"transactionId": "tx123", "status": "notified"}
    },
    {
        "topic": "pix.audit.log",
        "value": {"transactionId": "tx123", "action": "completed"}
    },
]

def send_event(url, event):
    response = requests.post(url, json=event)
    print(f"Sent to {url}: {response.status_code} - {response.json()}")

if __name__ == "__main__":
    while True:
        event = random.choice(pix_events)
        target = KAFKA_URL if 'payment' in event["topic"] else RABBIT_URL
        send_event(target, event)
        time.sleep(5)
```

---

# Como usar:

1. Suba toda a infra e as APIs no Kubernetes (como nas partes anteriores).
2. Em outro terminal, execute o consumer Kafka:

```bash
kubectl exec -n api-kafka -it deploy/api-kafka -- python consumer_kafka.py
```

3. Execute o consumer RabbitMQ:

```bash
kubectl exec -n api-rabbitmq -it deploy/api-rabbitmq -- python consumer_rabbit.py
```

4. Execute localmente o simulador (precisa do Python com `requests` instalado):

```bash
pip install requests
python simulator/send_events.py
```

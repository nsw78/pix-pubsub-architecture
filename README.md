### PROJETO PIX - KAFKA E RABBITMQ (PUB/SUB)


* `README.md` documentado para GitHub ✅
* Comandos de teste com `curl` ✅
* Execução no VSCode ✅
* (Extra) `docker-compose.yaml` para rodar localmente sem Kubernetes ✅

---

## 📝 `README.md`

```md
# 💳 PIX Pub/Sub Architecture with Kafka and RabbitMQ

Este projeto implementa uma arquitetura de mensageria para transações PIX simuladas, utilizando **Kafka** e **RabbitMQ** como mecanismos de Pub/Sub. Foi projetado para ambientes Kubernetes via **Minikube** com observabilidade integrada (Prometheus + Grafana + Alertmanager).

---

## 📁 Estrutura

```

pix-pubsub-architecture/
├── api-kafka/             # API Flask que envia eventos para Kafka
├── api-rabbitmq/          # API Flask que envia eventos para RabbitMQ
├── k8s/                   # Manifests Kubernetes
│   ├── kafka/
│   ├── rabbitmq/
│   ├── api-kafka/
│   ├── api-rabbitmq/
│   ├── ingress/
│   └── monitoring/
├── .gitignore
├── requirements.txt
└── README.md

````

---

## 🚀 Funcionalidade

Tópicos utilizados no padrão de mensageria PIX:

| Tópico / Routing Key         | Função                         |
|-----------------------------|--------------------------------|
| `pix.payment.requested`     | Início da transação            |
| `pix.payment.validated`     | Pós-antifraude                 |
| `pix.payment.settled`       | Liquidação confirmada          |
| `pix.notification.sent`     | Notificação enviada            |
| `pix.audit.log`             | Auditoria e rastreabilidade    |

---

## ✅ Pré-requisitos

- Minikube
- Helm
- Docker
- Kubectl
- VSCode com extensão Kubernetes

---

## ⚙️ Build das imagens

```bash
eval $(minikube docker-env)
docker build -t api-kafka:latest ./api-kafka
docker build -t api-rabbitmq:latest ./api-rabbitmq
````

---

## ☸️ Deploy no Kubernetes

```bash
minikube start --driver=docker
minikube addons enable ingress

kubectl apply -f k8s/namespaces.yaml
kubectl apply -f k8s/kafka/
kubectl apply -f k8s/rabbitmq/
kubectl apply -f k8s/api-kafka/
kubectl apply -f k8s/api-rabbitmq/
kubectl apply -f k8s/ingress/
kubectl apply -f k8s/monitoring/
```

---

## 🌐 Acessos

Ver IP:

```bash
minikube ip
```

| Serviço        | Porta       | Exemplo URL                  |
| -------------- | ----------- | ---------------------------- |
| API Kafka      | via ingress | `http://pix.local/kafka`     |
| API RabbitMQ   | via ingress | `http://pix.local/rabbit`    |
| Grafana        | 30300       | `http://<minikube-ip>:30300` |
| Prometheus     | 30090       | `http://<minikube-ip>:30090` |
| Alertmanager   | 30093       | `http://<minikube-ip>:30093` |
| RabbitMQ Panel | 15672       | `http://<minikube-ip>:15672` |

---

## 🧪 Testes com `curl`

### Enviar evento Kafka:

```bash
curl -X POST http://pix.local/kafka -H "Content-Type: application/json" -d '{
  "topic": "pix.payment.requested",
  "value": {
    "transactionId": "12345",
    "amount": 100,
    "payer": "alice",
    "receiver": "bob"
  }
}'
```

### Enviar evento RabbitMQ:

```bash
curl -X POST http://pix.local/rabbit -H "Content-Type: application/json" -d '{
  "topic": "pix.notification.sent",
  "value": {
    "transactionId": "12345",
    "status": "notified"
  }
}'
```

---

## 🧪 Rodar local com `docker-compose` (opcional)

```yaml
# docker-compose.yaml (adicione na raiz se desejar rodar fora do k8s)
version: '3'
services:
  kafka:
    image: bitnami/kafka:latest
    environment:
      - KAFKA_CFG_ZOOKEEPER_CONNECT=zookeeper:2181
      - KAFKA_CFG_LISTENERS=PLAINTEXT://:9092
      - KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092
    ports:
      - "9092:9092"
    depends_on:
      - zookeeper

  zookeeper:
    image: bitnami/zookeeper:latest
    ports:
      - "2181:2181"

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"

  api-kafka:
    build: ./api-kafka
    ports:
      - "5000:5000"
    depends_on:
      - kafka

  api-rabbitmq:
    build: ./api-rabbitmq
    ports:
      - "5001:5001"
    depends_on:
      - rabbitmq
```

> Para rodar:

```bash
docker-compose up --build
```

---

## ✅ Checklist final

* [x] Kafka com 5 tópicos de PIX
* [x] RabbitMQ com Exchange `pix` tipo `topic`
* [x] APIs Flask separadas (Kafka / Rabbit)
* [x] Dockerfiles prontos
* [x] Manifests Kubernetes completos
* [x] Ingress configurado
* [x] Monitoring com Prometheus, Grafana, Alertmanager
* [x] Documentação pronta (este README)


---

## 🧩 1. Dashboards Prometheus e Grafana (customizados)

### 📄 `grafana-datasource.yaml` (configMap opcional via Helm/Grafana Operator)

```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
```

### 📄 Dashboard JSON (exemplo básico para Kafka e RabbitMQ)

Salve como `grafana-dashboard-kafka-rabbit.json` (recomendo importar via painel):

```json
{
  "title": "PIX PubSub Metrics",
  "panels": [
    {
      "type": "graph",
      "title": "Kafka Request Rate",
      "targets": [
        {
          "expr": "rate(kafka_server_brokertopicmetrics_messages_in_total[1m])",
          "legendFormat": "{{topic}}",
          "refId": "A"
        }
      ]
    },
    {
      "type": "graph",
      "title": "RabbitMQ Message Published",
      "targets": [
        {
          "expr": "rate(rabbitmq_messages_published_total[1m])",
          "legendFormat": "{{queue}}",
          "refId": "B"
        }
      ]
    }
  ]
}
```

> Importe esse JSON manualmente no painel do Grafana (menu lateral → Dashboards → Import).

---

## ⚙️ 2. Scripts utilitários

### 📄 `scripts/create_kafka_topics.sh`

```bash
#!/bin/bash
NAMESPACE=api-kafka
POD=$(kubectl get pods -n $NAMESPACE -l app=kafka -o jsonpath="{.items[0].metadata.name}")

TOPICS=(
  pix.payment.requested
  pix.payment.validated
  pix.payment.settled
  pix.notification.sent
  pix.audit.log
)

for topic in "${TOPICS[@]}"; do
  echo "Creating topic: $topic"
  kubectl -n $NAMESPACE exec -it $POD -- kafka-topics.sh --create --topic $topic --bootstrap-server localhost:9092 --if-not-exists
done
```

> Execute: `chmod +x scripts/create_kafka_topics.sh && ./scripts/create_kafka_topics.sh`

---

### 📄 `scripts/health_check.sh`

```bash
#!/bin/bash

echo "Kafka API:"
curl -s -o /dev/null -w "%{http_code}\\n" http://pix.local/kafka

echo "RabbitMQ API:"
curl -s -o /dev/null -w "%{http_code}\\n" http://pix.local/rabbit

echo "Prometheus:"
curl -s -o /dev/null -w "%{http_code}\\n" http://$(minikube ip):30090

echo "Grafana:"
curl -s -o /dev/null -w "%{http_code}\\n" http://$(minikube ip):30300
```

---

## 🔐 3. Boas práticas para produção (checklist resumido)

| Categoria        | Ação Recomendada                                                   |
| ---------------- | ------------------------------------------------------------------ |
| **Segurança**    | Adicionar TLS no Ingress e autenticação nas APIs                   |
| **Kafka**        | Usar `Kafka SASL` + ACL para autenticação e controle               |
| **RabbitMQ**     | Criar usuários com permissões separadas por Exchange               |
| **Logs**         | Incluir `loguru` ou `structlog` nas APIs Flask                     |
| **Tracing**      | OpenTelemetry com Grafana Tempo ou Jaeger                          |
| **Persistência** | Usar PV/PVC em Kafka/RabbitMQ (não in-memory)                      |
| **CI/CD**        | Criar pipeline GitHub Actions com `docker build` + `kubectl apply` |
| **Auto Scaling** | Adicionar HPA baseado em CPU e fila de mensagens                   |

---

## 📁 4. Sugestão de organização final no GitHub

```bash
pix-pubsub-architecture/
├── api-kafka/
├── api-rabbitmq/
├── k8s/
├── scripts/                    # <=== novo
│   ├── create_kafka_topics.sh
│   └── health_check.sh
├── dashboards/                # <=== novo
│   └── grafana-dashboard-kafka-rabbit.json
├── docker-compose.yaml
├── requirements.txt
├── .gitignore
└── README.md
```

## ✅ Finalizamos!

Você agora tem uma arquitetura completa, com:

* APIs isoladas para Kafka e RabbitMQ
* Infraestrutura Kubernetes com boas práticas
* Observabilidade real com Prometheus e Grafana
* Ingress, namespace, build, testes e até script de health check


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


## 📌 Observação

Este projeto é uma simulação local de arquitetura Pub/Sub para mensageria de transações PIX. Para produção, recomenda-se uso de TLS, autenticação Kafka, RabbitMQ HA, observabilidade avançada (OpenTelemetry), logs estruturados e persistência.

---

## 👨‍💻 Autor

Nelson Walcow
\[SRE | DevOps | Engenharia de Dados | Cloud Specialist]





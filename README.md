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


## 📌 Observação

Este projeto é uma simulação local de arquitetura Pub/Sub para mensageria de transações PIX. Para produção, recomenda-se uso de TLS, autenticação Kafka, RabbitMQ HA, observabilidade avançada (OpenTelemetry), logs estruturados e persistência.

---

## 👨‍💻 Autor

Nelson Walcow
\[SRE | DevOps | Engenharia de Dados | Cloud Specialist]





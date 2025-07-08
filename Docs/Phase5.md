Perfeito! Chegamos à **parte 5/5**, com recursos extras que levam seu projeto a outro nível — com foco em **observabilidade real**, **boas práticas**, **scripts de automação** e **preparação para ambientes reais**.

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

---

## 📌 5. Dicas para o GitHub

* Marque com as tags: `#kafka`, `#rabbitmq`, `#kubernetes`, `#pix`, `#pubsub`, `#flask`, `#grafana`, `#devops`

---

## ✅ Finalizamos!

Você agora tem uma arquitetura completa, com:

* APIs isoladas para Kafka e RabbitMQ
* Infraestrutura Kubernetes com boas práticas
* Observabilidade real com Prometheus e Grafana
* Ingress, namespace, build, testes e até script de health check



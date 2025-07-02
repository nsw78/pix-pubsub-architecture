**monitoramento completo com Prometheus, Grafana e Alertmanager**, e ajustamos Kafka e RabbitMQ para os tópicos PIX.

---

## 🔭 `k8s/monitoring/prometheus-deployment.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s

    scrape_configs:
      - job_name: 'kubernetes-services'
        kubernetes_sd_configs:
          - role: endpoints
        relabel_configs:
          - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)
          - source_labels: [__address__, __meta_kubernetes_service_annotation_prometheus_io_port]
            action: replace
            regex: (.+):(?:\\d+);(.+)
            replacement: $1:$2
            target_label: __address__

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
        - name: prometheus
          image: prom/prometheus
          args:
            - --config.file=/etc/prometheus/prometheus.yml
          ports:
            - containerPort: 9090
          volumeMounts:
            - name: config-volume
              mountPath: /etc/prometheus/
      volumes:
        - name: config-volume
          configMap:
            name: prometheus-config
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: monitoring
spec:
  type: NodePort
  selector:
    app: prometheus
  ports:
    - port: 9090
      targetPort: 9090
      nodePort: 30090
```

---

## 📊 `k8s/monitoring/grafana-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
        - name: grafana
          image: grafana/grafana
          ports:
            - containerPort: 3000
---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: monitoring
spec:
  type: NodePort
  selector:
    app: grafana
  ports:
    - port: 3000
      targetPort: 3000
      nodePort: 30300
```

---

## 🚨 `k8s/monitoring/alertmanager-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: alertmanager
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: alertmanager
  template:
    metadata:
      labels:
        app: alertmanager
    spec:
      containers:
        - name: alertmanager
          image: prom/alertmanager
          args:
            - "--config.file=/etc/alertmanager/config.yml"
          ports:
            - containerPort: 9093
---
apiVersion: v1
kind: Service
metadata:
  name: alertmanager
  namespace: monitoring
spec:
  type: NodePort
  selector:
    app: alertmanager
  ports:
    - port: 9093
      targetPort: 9093
      nodePort: 30093
```

---

## ✅ Deploy no Minikube

```bash
kubectl create namespace monitoring
kubectl apply -f k8s/monitoring/
```

Acesse no navegador:

* **Grafana:** `http://<minikube-ip>:30300`
* **Prometheus:** `http://<minikube-ip>:30090`
* **Alertmanager:** `http://<minikube-ip>:30093`

Ver IP:

```bash
minikube ip
```

---

## ✅ Criar tópicos Kafka para PIX

```bash
kubectl -n api-kafka exec -it deploy/kafka -- bash

# Dentro do container:
kafka-topics.sh --create --topic pix.payment.requested --bootstrap-server localhost:9092
kafka-topics.sh --create --topic pix.payment.validated --bootstrap-server localhost:9092
kafka-topics.sh --create --topic pix.payment.settled --bootstrap-server localhost:9092
kafka-topics.sh --create --topic pix.notification.sent --bootstrap-server localhost:9092
kafka-topics.sh --create --topic pix.audit.log --bootstrap-server localhost:9092
```

---

## ✅ Criar Exchange do RabbitMQ

Acesse o painel RabbitMQ:

```bash
minikube service rabbitmq-service -n api-rabbitmq --url
```

1. Acesse via navegador o link com porta `15672`
2. Login padrão:

   * **user:** `guest`
   * **pass:** `guest`
3. Vá em **Exchanges → Add a new exchange**
4. Crie um Exchange chamado `pix` do tipo **topic**

Você pode também automatizar isso futuramente com `rabbitmqadmin` ou APIs.

---

## 🛠️ Build das Imagens e Push local

```bash
# No root do projeto
eval $(minikube docker-env)

docker build -t api-kafka:latest ./api-kafka
docker build -t api-rabbitmq:latest ./api-rabbitmq
```

---

## ✅ Próximos passos

Na **parte 4**, entregarei:

* `README.md` completo e comentado para GitHub
* Instruções de teste com `curl`
* Execução em VSCode
* Opcional: `docker-compose.yaml` para testes fora do Kubernetes



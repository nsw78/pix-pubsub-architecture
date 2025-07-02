Perfeito! Vamos à **parte 2/5**, com os **manifests do Kubernetes** segmentados por diretório, namespace e boas práticas. Cada bloco tem o respectivo código pronto para copiar/colar.

---

## 🧱 `k8s/namespaces.yaml`

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: api-kafka
---
apiVersion: v1
kind: Namespace
metadata:
  name: api-rabbitmq
---
apiVersion: v1
kind: Namespace
metadata:
  name: monitoring
```

---

## 🧩 `k8s/kafka/kafka-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kafka
  namespace: api-kafka
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kafka
  template:
    metadata:
      labels:
        app: kafka
    spec:
      containers:
        - name: kafka
          image: bitnami/kafka:latest
          ports:
            - containerPort: 9092
          env:
            - name: KAFKA_BROKER_ID
              value: "1"
            - name: KAFKA_CFG_ZOOKEEPER_CONNECT
              value: zookeeper:2181
            - name: KAFKA_CFG_LISTENERS
              value: PLAINTEXT://:9092
            - name: KAFKA_CFG_ADVERTISED_LISTENERS
              value: PLAINTEXT://kafka-service:9092
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zookeeper
  namespace: api-kafka
spec:
  replicas: 1
  selector:
    matchLabels:
      app: zookeeper
  template:
    metadata:
      labels:
        app: zookeeper
    spec:
      containers:
        - name: zookeeper
          image: bitnami/zookeeper:latest
          ports:
            - containerPort: 2181
```

---

## 🔌 `k8s/kafka/kafka-service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: kafka-service
  namespace: api-kafka
spec:
  selector:
    app: kafka
  ports:
    - name: kafka
      port: 9092
      targetPort: 9092
---
apiVersion: v1
kind: Service
metadata:
  name: zookeeper
  namespace: api-kafka
spec:
  selector:
    app: zookeeper
  ports:
    - name: zookeeper
      port: 2181
      targetPort: 2181
```

---

## 🐇 `k8s/rabbitmq/rabbitmq-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rabbitmq
  namespace: api-rabbitmq
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rabbitmq
  template:
    metadata:
      labels:
        app: rabbitmq
    spec:
      containers:
        - name: rabbitmq
          image: rabbitmq:3-management
          ports:
            - containerPort: 5672
            - containerPort: 15672
```

---

## 🔌 `k8s/rabbitmq/rabbitmq-service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: rabbitmq-service
  namespace: api-rabbitmq
spec:
  selector:
    app: rabbitmq
  ports:
    - name: amqp
      port: 5672
      targetPort: 5672
    - name: management
      port: 15672
      targetPort: 15672
```

---

## 🚀 `k8s/api-kafka/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-kafka
  namespace: api-kafka
spec:
  replicas: 1
  selector:
    matchLabels:
      app: api-kafka
  template:
    metadata:
      labels:
        app: api-kafka
    spec:
      containers:
        - name: api-kafka
          image: api-kafka:latest
          ports:
            - containerPort: 5000
```

---

## 🔌 `k8s/api-kafka/service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-kafka
  namespace: api-kafka
spec:
  selector:
    app: api-kafka
  ports:
    - port: 80
      targetPort: 5000
```

---

## 🚀 `k8s/api-rabbitmq/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-rabbitmq
  namespace: api-rabbitmq
spec:
  replicas: 1
  selector:
    matchLabels:
      app: api-rabbitmq
  template:
    metadata:
      labels:
        app: api-rabbitmq
    spec:
      containers:
        - name: api-rabbitmq
          image: api-rabbitmq:latest
          ports:
            - containerPort: 5001
```

---

## 🔌 `k8s/api-rabbitmq/service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-rabbitmq
  namespace: api-rabbitmq
spec:
  selector:
    app: api-rabbitmq
  ports:
    - port: 80
      targetPort: 5001
```

---

## 🌐 `k8s/ingress/ingress.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pix-ingress
  namespace: api-kafka
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - host: pix.local
      http:
        paths:
          - path: /kafka
            pathType: Prefix
            backend:
              service:
                name: api-kafka
                port:
                  number: 80
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pix-ingress
  namespace: api-rabbitmq
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - host: pix.local
      http:
        paths:
          - path: /rabbit
            pathType: Prefix
            backend:
              service:
                name: api-rabbitmq
                port:
                  number: 80
```

---

## ✅ Teste no seu Minikube:

```bash
minikube start --driver=docker
kubectl apply -f k8s/namespaces.yaml
kubectl apply -f k8s/kafka/
kubectl apply -f k8s/rabbitmq/
kubectl apply -f k8s/api-kafka/
kubectl apply -f k8s/api-rabbitmq/
kubectl apply -f k8s/ingress/
```

> ✅ Ative o Ingress no Minikube (se ainda não tiver ativado):

```bash
minikube addons enable ingress
```

---

### Próximo passo:

Na **parte 3**, vamos:

* Criar os manifestos para o **monitoramento com Prometheus, Grafana e Alertmanager**
* Adicionar os tópicos Kafka e Exchange no RabbitMQ para os eventos PIX
* Gerar os comandos para build das imagens



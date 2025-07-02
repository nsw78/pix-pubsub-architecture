#!/bin/bash
# Script para build das imagens Docker e push para o Minikube   
# Fonte de consulta: https://minikube.sigs.k8s.io/docs/handbook/docker-env/

# No root do projeto

eval $(minikube docker-env)

docker build -t api-kafka:latest ./api-kafka
docker build -t api-rabbitmq:latest ./api-rabbitmq

$folders = @(
    "pix-pubsub-architecture/api-kafka",
    "pix-pubsub-architecture/api-rabbitmq",
    "pix-pubsub-architecture/k8s/kafka",
    "pix-pubsub-architecture/k8s/rabbitmq",
    "pix-pubsub-architecture/k8s/api-kafka",
    "pix-pubsub-architecture/k8s/api-rabbitmq",
    "pix-pubsub-architecture/k8s/ingress",
    "pix-pubsub-architecture/k8s/monitoring",
    "pix-pubsub-architecture/docker"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Path $folder -Force
}

# Deployment Guide

## Prerequisites

- Ensure Docker, Kubernetes, and Helm are installed and configured.
- Access to a cloud environment (AWS, GCP, Azure) for deployment.
- Terraform and Helm are installed on the system.

## Steps

### 1. Clone the Repository

Clone the project repository from Git:

```bash
git clone https://github.com/repo.git
cd repo
```

### 2. Build Docker Images

Build Docker images for all services:

```bash
docker build -t service-a:latest ./services/service-a
docker build -t service-b:latest ./services/service-b
docker build -t api-gateway:latest ./api-gateway
```

### 3. Deploy Kubernetes Components

Ensure the Kubernetes cluster is up and running. Deploy the services:

```bash
kubectl apply -f ./services/service-a/deployment/k8s
kubectl apply -f ./services/service-b/deployment/k8s
kubectl apply -f ./api-gateway/deployment/k8s_gateway.yaml
```

### 4. Configure Ingress

Set up ingress to route external traffic to the services:

```bash
kubectl apply -f ./k8s/ingress.yaml
```

### 5. Apply Helm Charts for Service Mesh

Deploy Istio for service mesh:

```bash
helm install istio-base istio/base
helm install istio-ingress istio/ingress
```

### 6. Set up Observability

Deploy Prometheus and Grafana for monitoring:

```bash
kubectl apply -f ./monitoring/prometheus/prometheus.yaml
kubectl apply -f ./monitoring/grafana/dashboard_config.json
```

### 7. Configure CI/CD

The CI/CD pipeline for automated deployment uses ArgoCD. Apply the ArgoCD application:

```bash
kubectl apply -f ./ci-cd/argocd/application.yml
```

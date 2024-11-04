#!/bin/bash

# Exit script on any error
set -e

# Define variables
NAMESPACE="production"
DOCKER_REGISTRY="docker.io/username"
SERVICES=("service-a" "service-b" "api-gateway")
K8S_DEPLOY_DIR="deployment/k8s"
HELM_CHART_DIR="service-mesh/helm-charts/service-mesh-chart"

# Build Docker images for each service
for SERVICE in "${SERVICES[@]}"; do
    echo "Building Docker image for ${SERVICE}..."
    docker build -t "${DOCKER_REGISTRY}/${SERVICE}:latest" ./services/${SERVICE}
    echo "Pushing Docker image for ${SERVICE} to registry..."
    docker push "${DOCKER_REGISTRY}/${SERVICE}:latest"
done

# Apply Kubernetes deployments for services
for SERVICE in "${SERVICES[@]}"; do
    echo "Deploying ${SERVICE} to Kubernetes..."
    kubectl apply -f ./services/${SERVICE}/${K8S_DEPLOY_DIR}/deployment.yaml -n $NAMESPACE
    kubectl apply -f ./services/${SERVICE}/${K8S_DEPLOY_DIR}/service.yaml -n $NAMESPACE
done

# Deploy the API Gateway
echo "Deploying API Gateway to Kubernetes..."
kubectl apply -f ./api-gateway/deployment/k8s_gateway.yaml -n $NAMESPACE

# Deploy Service Mesh using Helm
echo "Deploying Service Mesh using Helm..."
helm upgrade --install service-mesh ${HELM_CHART_DIR} --namespace $NAMESPACE

# Verify the deployments
echo "Verifying deployments..."
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE

echo "Deployment completed successfully."
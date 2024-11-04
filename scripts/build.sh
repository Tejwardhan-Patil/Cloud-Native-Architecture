#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define the root directory
ROOT_DIR=$(dirname "$0")/..

# Load configurations based on environment (default is 'dev')
ENV=${1:-dev}
CONFIG_FILE="$ROOT_DIR/configs/config.$ENV.yaml"

echo "Building the project with configuration: $CONFIG_FILE"

# Check if configuration file exists
if [ ! -f "$CONFIG_FILE" ]; then
  echo "Configuration file $CONFIG_FILE not found!"
  exit 1
fi

# Build Service A
echo "Building Service A..."
cd "$ROOT_DIR/services/service-a"
go build -o service-a ./src/main.go
echo "Service A built successfully."

# Build Service B
echo "Building Service B..."
cd "$ROOT_DIR/services/service-b"
mvn clean package
echo "Service B built successfully."

# Build API Gateway
echo "Building API Gateway..."
cd "$ROOT_DIR/api-gateway"
go build -o api-gateway ./src/gateway.go
echo "API Gateway built successfully."

# Docker build for all services
echo "Building Docker images..."
cd "$ROOT_DIR"

docker build -t service-a:latest ./services/service-a
docker build -t service-b:latest ./services/service-b
docker build -t api-gateway:latest ./api-gateway

echo "Docker images built successfully."

# Success message
echo "Project build completed."
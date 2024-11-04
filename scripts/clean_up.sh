#!/bin/bash

# Log file location
LOG_FILE="/var/log/cleanup.log"

# Timestamp for logging
timestamp() {
  date +"%Y-%m-%d %H:%M:%S"
}

# Log function for cleaner output
log_message() {
  echo "$(timestamp): $1" | tee -a "$LOG_FILE"
}

# Function to clean up Kubernetes resources
cleanup_k8s() {
  log_message "Starting Kubernetes resources cleanup..."
  kubectl delete all --all --namespace=default
  if [ $? -eq 0 ]; then
    log_message "Successfully cleaned up Kubernetes resources."
  else
    log_message "Error occurred while cleaning up Kubernetes resources."
  fi
}

# Function to clean up Docker containers and images
cleanup_docker() {
  log_message "Starting Docker cleanup..."
  
  # Stop and remove all containers
  docker ps -aq | xargs docker stop
  docker ps -aq | xargs docker rm

  # Remove dangling images
  docker images -f "dangling=true" -q | xargs docker rmi

  if [ $? -eq 0 ]; then
    log_message "Docker cleanup completed successfully."
  else
    log_message "Error occurred during Docker cleanup."
  fi
}

# Function to remove temporary files
cleanup_temp_files() {
  log_message "Cleaning up temporary files..."
  find /tmp -type f -atime +7 -delete
  find /var/tmp -type f -atime +7 -delete

  if [ $? -eq 0 ]; then
    log_message "Temporary files cleaned up successfully."
  else
    log_message "Error occurred while cleaning temporary files."
  fi
}

# Execution starts here
log_message "Starting resource cleanup process."

cleanup_k8s
cleanup_docker
cleanup_temp_files

log_message "Resource cleanup process completed."
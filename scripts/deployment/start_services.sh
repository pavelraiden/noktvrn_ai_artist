#!/bin/bash

# Deployment Script: Start All Services
# Usage: ./scripts/deployment/start_services.sh [compose_file]
# Example: ./scripts/deployment/start_services.sh docker-compose.prod.yml

set -e

COMPOSE_FILE=${1:-docker-compose.yml} # Default to docker-compose.yml

SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")
PROJECT_ROOT=$(realpath "${SCRIPT_DIR}/../..")

echo "Changing directory to project root: ${PROJECT_ROOT}"
cd "${PROJECT_ROOT}"

echo "Starting all services defined in ${COMPOSE_FILE} in detached mode..."
docker compose -f "${COMPOSE_FILE}" up -d

echo "Services started. Use 'docker compose -f ${COMPOSE_FILE} ps' to check status."


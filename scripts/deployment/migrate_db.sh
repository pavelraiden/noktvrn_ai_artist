#!/bin/bash

# Deployment Script: Apply Database Migrations
# Usage: ./scripts/deployment/migrate_db.sh [compose_file]
# Example: ./scripts/deployment/migrate_db.sh docker-compose.prod.yml

set -e

COMPOSE_FILE=${1:-docker-compose.yml} # Default to docker-compose.yml
SERVICE_NAME="api" # The service container where alembic runs

SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")
PROJECT_ROOT=$(realpath "${SCRIPT_DIR}/../..")

echo "Changing directory to project root: ${PROJECT_ROOT}"
cd "${PROJECT_ROOT}"

# Ensure the API service container is running or start it if needed
# Note: This assumes the DB service is also started by compose
if [ -z "$(docker compose -f "${COMPOSE_FILE}" ps -q ${SERVICE_NAME})" ] || [ "$(docker compose -f "${COMPOSE_FILE}" ps -q ${SERVICE_NAME} | xargs docker inspect -f '{{.State.Status}}')" != "running" ]; then
  echo "API service container is not running. Starting services..."
  docker compose -f "${COMPOSE_FILE}" up -d db ${SERVICE_NAME}
  # Add a small delay to allow the service to initialize
  sleep 10
fi

echo "Applying Alembic migrations inside the '${SERVICE_NAME}' container..."
docker compose -f "${COMPOSE_FILE}" exec "${SERVICE_NAME}" alembic upgrade head

echo "Database migrations applied successfully."


#!/bin/bash

# Deployment Script: Build and Push Docker Image
# Usage: ./scripts/deployment/build_push.sh <image_tag> [registry_prefix]
# Example: ./scripts/deployment/build_push.sh v1.0.0 ghcr.io/your_username

set -e # Exit immediately if a command exits with a non-zero status.

IMAGE_TAG=${1:-latest}
REGISTRY_PREFIX=${2:-your_dockerhub_username} # Replace with your default registry/username
IMAGE_NAME="ai-artist-api"
FULL_IMAGE_NAME="${REGISTRY_PREFIX}/${IMAGE_NAME}:${IMAGE_TAG}"

SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")
PROJECT_ROOT=$(realpath "${SCRIPT_DIR}/../..")

echo "Changing directory to project root: ${PROJECT_ROOT}"
cd "${PROJECT_ROOT}"

echo "Building Docker image: ${FULL_IMAGE_NAME}"
docker build -t "${FULL_IMAGE_NAME}" -f Dockerfile .

echo "Docker image built successfully: ${FULL_IMAGE_NAME}"

# Optional: Push the image to the registry
read -p "Do you want to push the image to ${REGISTRY_PREFIX}? (y/N) " -n 1 -r
echo # Move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Logging in to registry (if required)..."
    # Add login command if necessary, e.g., docker login ghcr.io -u USERNAME -p TOKEN
    # Or assume user is already logged in

    echo "Pushing image: ${FULL_IMAGE_NAME}"
    docker push "${FULL_IMAGE_NAME}"
    echo "Image pushed successfully."
else
    echo "Skipping image push."
fi

echo "Build and Push script finished."


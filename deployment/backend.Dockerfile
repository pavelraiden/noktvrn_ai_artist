# Backend Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (if any)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
# Note: Adjust this if your structure is different or for production builds
COPY . .

# Set the working directory within the project structure if needed
WORKDIR /app/ai_artist_system_clone

# Expose ports if the backend runs a server directly (unlikely if using batch runner)
# EXPOSE 8000

# Default command (can be overridden in docker-compose.yml)
# CMD ["python3.11", "your_main_script.py"]


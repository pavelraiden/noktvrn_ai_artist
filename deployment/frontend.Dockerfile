# Frontend Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (if any)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Copy requirements first for layer caching
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the frontend application code
COPY src/ src/

# Expose the port the app runs on
EXPOSE 5000

# Set environment variables (can be overridden in docker-compose)
ENV FLASK_ENV=production

# Command to run the application using Gunicorn
# Ensure src/main.py defines the Flask app instance as `app`
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "src.main:app"]


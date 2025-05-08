# AI Artist System Deployment Setup Guide

This guide provides instructions for setting up the AI Artist System for local development or a production-like environment using Docker and Docker Compose.

## Prerequisites

*   **Docker:** Install Docker Engine (refer to [official Docker documentation](https://docs.docker.com/engine/install/)).
*   **Docker Compose:** Install Docker Compose (refer to [official Docker documentation](https://docs.docker.com/compose/install/)).
*   **Git:** Required to clone the repository.
*   **Environment Variables:** You will need API keys and credentials for external services (OpenAI, Spotify). See the Configuration Guide for details.

## 1. Clone the Repository

```bash
git clone <repository_url> # Replace with the actual repository URL
cd nokturn_ai_artist # Navigate to the project root directory
```

## 2. Configure Environment Variables

Create a `.env` file in the project root directory (`/home/ubuntu/ai_artist_system/noktvrn_ai_artist/`). This file will store sensitive credentials and configuration settings.

Copy the example environment file if one exists, or create a new one with the following content, replacing placeholder values with your actual credentials:

```dotenv
# PostgreSQL Settings
POSTGRES_DB=ai_artist_db
POSTGRES_USER=ai_artist_user
POSTGRES_PASSWORD=changeme # Use a strong password

# External API Keys
OPENAI_API_KEY=your_openai_api_key
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# Grafana Admin (Optional - for local dev)
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin # Change for production

# Add any other required environment variables here...
```

**Important:** Add `.env` to your `.gitignore` file to prevent committing sensitive information.

## 3. Build and Run with Docker Compose

From the project root directory, run the following command:

```bash
docker compose up --build -d
```

*   `--build`: Forces Docker Compose to build the images defined in the `docker-compose.yml` file (e.g., the `api` service image).
*   `-d`: Runs the containers in detached mode (in the background).

This command will:

1.  Pull the necessary base images (Python, PostgreSQL, Prometheus, Grafana).
2.  Build the custom `api` service image based on the `Dockerfile`.
3.  Create and start containers for all defined services (`db`, `api`, `prometheus`, `grafana`).
4.  Create the necessary Docker volumes for persistent data.
5.  Connect the containers to the defined Docker networks.

## 4. Verify the Setup

*   **Check Running Containers:**
    ```bash
    docker compose ps
    ```
    You should see all services (`db`, `api`, `prometheus`, `grafana`) listed with a status of `running` or `healthy`.

*   **Access API:** Open your web browser or use `curl` to access the API root endpoint:
    *   URL: `http://localhost:8000/`
    *   You should receive a JSON response like: `{"message":"Welcome to the AI Artist System API"}`

*   **Access API Docs:**
    *   URL: `http://localhost:8000/docs`
    *   You should see the FastAPI Swagger UI documentation.

*   **Access Grafana:**
    *   URL: `http://localhost:3000/`
    *   Login with the credentials defined in your `.env` file (default: admin/admin).

*   **Access Prometheus:**
    *   URL: `http://localhost:9090/`
    *   You can explore metrics and targets.

## 5. Database Migrations (Using Alembic)

Database schema migrations are managed using Alembic. To apply migrations:

1.  **Initialize Alembic (One-time setup):**
    *   Ensure Alembic is installed (`pip install alembic`).
    *   Run `alembic init alembic` in the project root (if not already done).
    *   Configure `alembic.ini` and `alembic/env.py` to connect to your database (using environment variables is recommended).

2.  **Apply Migrations:**
    *   Run migrations inside the running `api` container:
        ```bash
        docker compose exec api alembic upgrade head
        ```
    *   Alternatively, if Alembic is configured to read environment variables correctly, you might run it locally if you have direct access to the database port (e.g., `DATABASE_URL=postgresql://ai_artist_user:changeme@localhost:5432/ai_artist_db alembic upgrade head`).

## 6. Stopping the Environment

To stop the running containers:

```bash
docker compose down
```

To stop and remove volumes (useful for a clean restart, **will delete database data**):

```bash
docker compose down -v
```

This concludes the basic setup guide for the AI Artist System using Docker Compose.


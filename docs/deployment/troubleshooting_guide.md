# AI Artist System Troubleshooting Guide

This guide provides solutions to common problems encountered during the setup and operation of the AI Artist System using Docker Compose.

## Docker & Docker Compose Issues

*   **Problem:** `docker compose up` fails with errors related to network conflicts or port already in use.
    *   **Cause:** Another application or Docker container might be using the ports required by the AI Artist System (e.g., 5432 for PostgreSQL, 8000 for API, 9090 for Prometheus, 3000 for Grafana).
    *   **Solution:**
        1.  Identify the conflicting process: Use `sudo lsof -i :<port_number>` or `netstat -tulnp | grep <port_number>` to find the process using the port.
        2.  Stop the conflicting process or container.
        3.  Alternatively, change the host port mapping in `docker-compose.yml`. For example, change `ports: - "8000:8000"` to `ports: - "8080:8000"` to access the API on `http://localhost:8080`.

*   **Problem:** `docker compose up` fails with errors like "Cannot connect to the Docker daemon".
    *   **Cause:** The Docker daemon is not running or your user doesn't have permission to access it.
    *   **Solution:**
        1.  Ensure the Docker service is running: `sudo systemctl status docker`.
        2.  Start the Docker service if stopped: `sudo systemctl start docker`.
        3.  Add your user to the `docker` group (requires logout/login or new shell): `sudo usermod -aG docker $USER`.

*   **Problem:** Docker image build fails (`docker compose up --build`).
    *   **Cause:** Errors in the `Dockerfile` (e.g., missing dependencies, incorrect commands), network issues preventing package downloads, insufficient disk space.
    *   **Solution:**
        1.  Carefully read the error messages during the build process.
        2.  Check the `Dockerfile` for syntax errors or incorrect commands.
        3.  Ensure you have a stable internet connection.
        4.  Check available disk space: `df -h`.
        5.  Try building step-by-step or commenting out sections of the `Dockerfile` to isolate the issue.

## Application & Service Issues

*   **Problem:** The `api` service fails to start or keeps restarting.
    *   **Cause:** Incorrect environment variables (especially `DATABASE_URL`), code errors in the FastAPI application, database connection issues, missing Python dependencies.
    *   **Solution:**
        1.  Check the container logs: `docker compose logs api`.
        2.  Verify the `.env` file has the correct values and format.
        3.  Ensure the `db` service is running and healthy: `docker compose ps`.
        4.  Check for syntax errors or runtime exceptions in the application code.
        5.  Ensure all dependencies in `requirements.txt` are installed correctly during the build.

*   **Problem:** The `db` (PostgreSQL) service fails to start or is unhealthy.
    *   **Cause:** Data volume permission issues, corrupted data files, incorrect `POSTGRES_` environment variables.
    *   **Solution:**
        1.  Check the container logs: `docker compose logs db`.
        2.  Ensure the `postgres_data` volume has correct permissions.
        3.  Try stopping and removing the volume (`docker compose down -v`) and restarting (`docker compose up -d`). **Warning: This deletes all database data.**
        4.  Verify the `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` variables in `.env` are correctly set.

*   **Problem:** Cannot connect to the database from the `api` service.
    *   **Cause:** Incorrect `DATABASE_URL` in the `api` service environment, network issues between containers, `db` service not ready.
    *   **Solution:**
        1.  Verify the `DATABASE_URL` format and credentials.
        2.  Ensure both `api` and `db` containers are on the same Docker network (`backend` in the provided `docker-compose.yml`).
        3.  Check the `db` service healthcheck status in `docker compose ps`.
        4.  Check `api` logs for specific connection error messages.

*   **Problem:** Grafana or Prometheus is not accessible or showing errors.
    *   **Cause:** Container failed to start, configuration file errors (`prometheus.yml`), volume permission issues.
    *   **Solution:**
        1.  Check container logs: `docker compose logs grafana` or `docker compose logs prometheus`.
        2.  Verify the syntax and paths in `prometheus.yml`.
        3.  Ensure data volumes (`grafana_data`, `prometheus_data`) have correct permissions.
        4.  Check network connectivity between containers if Grafana cannot reach Prometheus.

## Alembic Migration Issues

*   **Problem:** `alembic upgrade head` fails.
    *   **Cause:** Database connection issues, incorrect Alembic configuration (`alembic.ini`, `env.py`), conflicts between migration scripts and the current database state.
    *   **Solution:**
        1.  Ensure the database container is running and accessible.
        2.  Verify the `sqlalchemy.url` in `alembic.ini` or how `env.py` constructs the connection string (it should use the `DATABASE_URL` environment variable if running inside the container).
        3.  Check the specific error message from Alembic.
        4.  Inspect the `alembic_version` table in the database to see the current revision.
        5.  If necessary, manually resolve conflicts or downgrade/stamp the database version.

This guide covers common issues. For more specific problems, consult the logs of the affected service (`docker compose logs <service_name>`) and refer to the documentation of the specific tools (Docker, PostgreSQL, FastAPI, Alembic, etc.).


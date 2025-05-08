# AI Artist System Configuration Guide

This document details the environment variables required to configure the AI Artist System.

## Overview

The system relies on environment variables for configuration, especially for sensitive information like database credentials and API keys. These variables are typically loaded from a `.env` file in the root directory during local development using Docker Compose, or injected directly into the container environment in production.

Refer to the `docker-compose.yml` file and the `Setup Guide` for context on how these variables are used.

## Core Application Variables (`api` service)

These variables are primarily used by the FastAPI application and its underlying modules.

*   `DATABASE_URL`
    *   **Description:** The connection string for the PostgreSQL database.
    *   **Format:** `postgresql://<user>:<password>@<host>:<port>/<database>`
    *   **Example (Docker Compose):** `postgresql://ai_artist_user:changeme@db:5432/ai_artist_db` (Set automatically in `docker-compose.yml` based on other variables)
    *   **Required:** Yes

*   `OPENAI_API_KEY`
    *   **Description:** Your API key for accessing OpenAI services (used by the LLM Orchestrator).
    *   **Example:** `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
    *   **Required:** Yes (for LLM features)

*   `SPOTIFY_CLIENT_ID`
    *   **Description:** Your client ID for the Spotify API (used for fetching chart data, track features, etc.).
    *   **Example:** `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
    *   **Required:** Yes (for Spotify integration)

*   `SPOTIFY_CLIENT_SECRET`
    *   **Description:** Your client secret for the Spotify API.
    *   **Example:** `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
    *   **Required:** Yes (for Spotify integration)

*   `LOGGING_LEVEL` (Optional)
    *   **Description:** Sets the root logging level for the application.
    *   **Values:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
    *   **Default:** `INFO` (as set in `logging_config.json`)

## Database Service Variables (`db` service - PostgreSQL)

These variables configure the PostgreSQL container itself.

*   `POSTGRES_DB`
    *   **Description:** The name of the database to create.
    *   **Default (in `docker-compose.yml`):** `ai_artist_db`
    *   **Required:** Yes

*   `POSTGRES_USER`
    *   **Description:** The username for the database superuser.
    *   **Default (in `docker-compose.yml`):** `ai_artist_user`
    *   **Required:** Yes

*   `POSTGRES_PASSWORD`
    *   **Description:** The password for the database superuser.
    *   **Default (in `docker-compose.yml`):** `changeme` ( **MUST be changed for production**)
    *   **Required:** Yes

## Monitoring Service Variables (`grafana` service)

These variables configure the Grafana monitoring dashboard container.

*   `GRAFANA_ADMIN_USER`
    *   **Description:** The username for the Grafana admin user.
    *   **Default (in `docker-compose.yml`):** `admin`
    *   **Required:** No (defaults provided)

*   `GRAFANA_ADMIN_PASSWORD`
    *   **Description:** The password for the Grafana admin user.
    *   **Default (in `docker-compose.yml`):** `admin` ( **Should be changed for production**)
    *   **Required:** No (defaults provided)

## Loading Configuration

*   **Local Development (Docker Compose):** Create a `.env` file in the project root. Docker Compose automatically loads variables from this file.
*   **Production:** Inject these environment variables into your container runtime environment using your orchestrator's mechanisms (e.g., Kubernetes Secrets/ConfigMaps, environment variables in task definitions, etc.). **Do not commit `.env` files containing production secrets to version control.**

